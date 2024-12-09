"""
LangChain model pool manager.
This module provides a pool manager for LangChain models, handling the lifecycle
and concurrent access of model instances.
"""

from typing import Dict, Optional, List, Final
import asyncio
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from asyncio_pool import AioPool
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from app.services.model_service import ModelService
from app.repositories.model_repository import ModelRepository
from app.repositories.model_provider_repository import ModelProviderRepository
from app.repositories.models import Model
from app.core.logging import logger
from app.core.database import SessionLocal


@dataclass
class ModelPoolConfig:
    """ModelPool的配置数据类"""
    model_instances: Dict[str, BaseChatModel] = field(default_factory=dict)
    model_configs: Dict[str, Model] = field(default_factory=dict)
    semaphores: Dict[str, asyncio.Semaphore] = field(default_factory=dict)
    instance_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    task_pool: AioPool = field(default_factory=lambda: AioPool(
        size=ModelPool.DEFAULT_POOL_SIZE))

    async def get_semaphore_value(self, deploy_name: str) -> int:
        """获取信号量的当前值"""
        semaphore = self.semaphores.get(deploy_name)
        if semaphore is None:
            return 0
        # 信号量的_value属性表示当前可用的槽位数
        return semaphore._value


class ModelPool:
    """
    LangChain模型池管理类

    负责维护和管理所有模型实例，提供线程安全的模型访问机制。
    使用 asyncio_pool 来控制并发访问，确保每个模型的资源使用在限制范围内。
    """

    DEFAULT_POOL_SIZE: Final = 3
    _instance: Optional['ModelPool'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    def __init__(self):
        """初始化方法是私有的，请使用 get_instance() 或 initialize() 方法获取实例"""
        # 初始化服务和依赖
        self._db = SessionLocal()
        self.model_repository = ModelRepository(self._db)
        self.provider_repository = ModelProviderRepository(self._db)
        self.model_service = ModelService(
            self.model_repository, self.provider_repository)

        # 使用数据类来管理配置
        self._config = ModelPoolConfig()

    def get_db(self):
        """获取数据库会话"""
        return self._db

    def close_db(self):
        """关闭数据库连接"""
        if self._db:
            self._db.close()

    @classmethod
    async def initialize(cls) -> 'ModelPool':
        """初始化ModelPool单例"""
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls()
                cls._initialized = True
                await cls._instance.initialize_pools()
            return cls._instance

    @classmethod
    async def get_instance(cls) -> 'ModelPool':
        """获取ModelPool单例实例"""
        if not cls._initialized:
            raise RuntimeError(
                "ModelPool not initialized. Call initialize() first")
        return cls._instance

    async def initialize_pools(self):
        """初始化所有模型池"""
        async with self._config.instance_lock:
            active_models = self.model_service.get_active_models()
            for model in active_models:
                await self._initialize_model(model)

    async def _initialize_model(self, model: Model):
        """初始化单个模型"""
        if model.deploy_name in self._config.model_instances:
            return

        # 创建模型实例
        instance = self._create_model_instance(model)
        # 创建并发控制信号量
        semaphore = asyncio.Semaphore(self.DEFAULT_POOL_SIZE)

        self._config.model_instances[model.deploy_name] = instance
        self._config.model_configs[model.deploy_name] = model
        self._config.semaphores[model.deploy_name] = semaphore

        logger.info(
            f"Initialized model {model.deploy_name} with concurrency limit {self.DEFAULT_POOL_SIZE}")

    def get_config(self) -> ModelPoolConfig:
        """获取模型池配置"""
        return self._config

    def get_model_instance(self, deploy_name: str) -> Optional[BaseChatModel]:
        """获取模型实例"""
        return self._config.model_instances.get(deploy_name)

    def get_model_config(self, deploy_name: str) -> Optional[Model]:
        """获取模型配置"""
        return self._config.model_configs.get(deploy_name)

    def has_model(self, deploy_name: str) -> bool:
        """检查模型是否在池中"""
        return deploy_name in self._config.model_instances

    async def get_semaphore(self, deploy_name: str) -> Optional[asyncio.Semaphore]:
        """获取模型的信号量"""
        return self._config.semaphores.get(deploy_name)

    @asynccontextmanager
    async def get_model(self, deploy_name: str):
        """
        获取模型实例的上下文管理器

        使用方式：
        async with model_pool.get_model("gpt-3.5-turbo") as model:
            result = await model.agenerate(["Your prompt"])
        """
        if not self.has_model(deploy_name):
            raise ValueError(f"Model {deploy_name} not found in pool")

        semaphore = await self.get_semaphore(deploy_name)
        model = self.get_model_instance(deploy_name)

        async def _use_model():
            async with semaphore:
                return model

        try:
            # 在任务池中执行模型操作
            instance = await (await self._config.task_pool.spawn(_use_model()))
            yield instance
        finally:
            # 这里可以添加一些清理逻辑，如果需要的话
            pass

    async def refresh_model(self, deploy_name: str):
        """
        刷新指定模型
        - 如果模型在池中存在，使用最新配置更新模型
        - 如果模型在池中不存在但在数据库中存在，则添加到池中
        - 如果模型在数据库中不存在，则抛出异常
        Args:
            deploy_name: 模型的部署名称
        Raises:
            ValueError: 当模型在数据库中不存在时抛出
        """
        async with self._config.instance_lock:
            # 获取最新的模型配置
            model = self.model_service.get_by_deploy_name(deploy_name)
            if not model:
                raise ValueError(f"Model {deploy_name} not found in database")

            # 检查模型是否在池中
            if not self.has_model(deploy_name):
                # 模型不在池中但在数据库中存在，添加到池中
                await self._initialize_model(model)
                logger.info(f"Added new model to pool: {deploy_name}")
                return

            # 模型在池中存在，更新配置
            # 等待当前任务完成
            semaphore = await self.get_semaphore(deploy_name)
            async with semaphore:
                # 更新模型实例
                self._config.model_instances[deploy_name] = self._create_model_instance(model)
                self._config.model_configs[deploy_name] = model
                logger.info(f"Refreshed model {deploy_name}")

    async def refresh_pool(self) -> Dict[str, List[str]]:
        """
        刷新模型池，比较数据库中的模型和池中的模型
        - 如果有新模型则添加到池中
        - 如果有已删除的模型则从池中移除
        - 如果现有模型配置发生变化则重新加载配置
        Returns:
            Dict包含添加、移除和更新的模型deploy_name列表
        """
        async with self._config.instance_lock:
            # 获取数据库中的所有激活模型
            active_models = self.model_service.get_active_models()
            active_models_dict = {model.deploy_name: model for model in active_models}
            active_deploy_names = set(active_models_dict.keys())
            pool_deploy_names = set(self._config.model_instances.keys())

            # 找出需要添加和移除的模型
            to_add = active_deploy_names - pool_deploy_names
            to_remove = pool_deploy_names - active_deploy_names
            # 找出需要检查配置的现有模型
            to_check = pool_deploy_names & active_deploy_names

            # 添加新模型
            added_models = []
            for deploy_name in to_add:
                model = active_models_dict[deploy_name]
                await self._initialize_model(model)
                added_models.append(deploy_name)
                logger.info(f"Added new model to pool: {deploy_name}")

            # 移除已删除的模型
            removed_models = []
            for deploy_name in to_remove:
                # 等待当前任务完成
                semaphore = await self.get_semaphore(deploy_name)
                async with semaphore:
                    # 移除模型实例和相关资源
                    self._config.model_instances.pop(deploy_name)
                    self._config.model_configs.pop(deploy_name)
                    self._config.semaphores.pop(deploy_name)
                    removed_models.append(deploy_name)
                    logger.info(f"Removed model from pool: {deploy_name}")

            # 检查并更新现有模型的配置
            updated_models = []
            for deploy_name in to_check:
                current_config = self.get_model_config(deploy_name)
                new_config = active_models_dict[deploy_name]
                # 比较配置是否发生变化
                if (current_config.properties != new_config.properties or
                    current_config.name != new_config.name or
                    current_config.provider != new_config.provider):
                    # 等待当前任务完成后更新配置
                    semaphore = await self.get_semaphore(deploy_name)
                    async with semaphore:
                        # 更新模型实例和配置
                        self._config.model_instances[deploy_name] = self._create_model_instance(new_config)
                        self._config.model_configs[deploy_name] = new_config
                        updated_models.append(deploy_name)
                        logger.info(f"Updated model configuration: {deploy_name}")

            return {
                "added": added_models,
                "removed": removed_models,
                "updated": updated_models
            }

    async def get_pool_status(self) -> List[Dict]:
        """获取所有模型池的状态信息"""
        status = []
        for deploy_name in self._config.model_instances.keys():
            config = self.get_model_config(deploy_name)
            available_slots = await self._config.get_semaphore_value(deploy_name)
            status.append({
                'deploy_name': deploy_name,
                'name': config.name,
                'provider': config.provider,
                'concurrency_limit': self.DEFAULT_POOL_SIZE,
                'available_slots': available_slots
            })
        return status

    @classmethod
    async def cleanup(cls):
        """清理所有资源"""
        if cls._instance:
            instance_config = cls._instance.get_config()
            async with instance_config.instance_lock:
                # 等待所有任务完成
                await instance_config.task_pool.join()

                # 清理资源
                instance_config.model_instances.clear()
                instance_config.model_configs.clear()
                instance_config.semaphores.clear()

                # 关闭数据库连接
                cls._instance.close_db()

                logger.info("Cleaned up all model pool resources")
                cls._initialized = False
                cls._instance = None

    def _create_model_instance(self, model: Model) -> BaseChatModel:
        """根据模型配置创建新的模型实例"""
        if model.provider == 'openai':
            return self._create_openai_instance(model)
        elif model.provider == 'azure_openai':
            return self._create_azure_openai_instance(model)
        raise ValueError(f"Unsupported model provider: {model.provider}")

    @staticmethod
    def _create_openai_instance(model: Model) -> BaseChatModel:
        """创建OpenAI模型实例"""
        return ChatOpenAI(
            model=model.properties.get('model'),
            api_key=model.properties.get('api_key'),
            base_url=model.properties.get('base_url'),
        )

    @staticmethod
    def _create_azure_openai_instance(model: Model) -> BaseChatModel:
        """创建Azure OpenAI模型实例"""
        return AzureChatOpenAI(
            azure_endpoint=model.properties.get('endpoint'),
            azure_deployment=model.properties.get('deployment_name'),
            openai_api_version=model.properties.get('openai_api_version'),
        )
