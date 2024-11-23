"""
LangChain model pool manager.
This module provides a pool manager for LangChain models, handling the lifecycle
and concurrent access of model instances.
"""

from typing import Dict, Optional, List, Final
import asyncio
from asyncio_pool import AioPool
from contextlib import asynccontextmanager
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from app.services.model_service import ModelService
from app.repositories.model_repository import ModelRepository
from app.repositories.model_provider_repository import ModelProviderRepository
from app.repositories.models import Model
from app.core.logging import logger
from app.core.database import SessionLocal


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

        # 模型实例池
        self._model_instances: Dict[str, BaseChatModel] = {}
        # 模型配置缓存
        self._model_configs: Dict[str, Model] = {}
        # 并发控制池，每个模型一个信号量
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        # 用于保护模型池操作的锁
        self._instance_lock = asyncio.Lock()
        # 任务池，用于并发控制
        self._task_pool = AioPool(size=self.DEFAULT_POOL_SIZE)

    @classmethod
    async def initialize(cls) -> 'ModelPool':
        """初始化ModelPool单例"""
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls()
                cls._initialized = True
                await cls._instance._initialize_pools()
            return cls._instance

    @classmethod
    async def get_instance(cls) -> 'ModelPool':
        """获取ModelPool单例实例"""
        if not cls._initialized:
            raise RuntimeError(
                "ModelPool not initialized. Call initialize() first")
        return cls._instance

    async def _initialize_pools(self):
        """初始化所有模型池"""
        async with self._instance_lock:
            active_models = self.model_service.get_active_models()
            for model in active_models:
                await self._initialize_model(model)

    async def _initialize_model(self, model: Model):
        """初始化单个模型"""
        if model.deploy_name in self._model_instances:
            return

        # 创建模型实例
        instance = self._create_model_instance(model)
        # 创建并发控制信号量
        semaphore = asyncio.Semaphore(self.DEFAULT_POOL_SIZE)

        self._model_instances[model.deploy_name] = instance
        self._model_configs[model.deploy_name] = model
        self._semaphores[model.deploy_name] = semaphore

        logger.info(
            f"Initialized model {model.deploy_name} with concurrency limit {self.DEFAULT_POOL_SIZE}")

    @asynccontextmanager
    async def get_model(self, deploy_name: str):
        """
        获取模型实例的上下文管理器

        使用方式：
        async with model_pool.get_model("gpt-3.5-turbo") as model:
            result = await model.agenerate(["Your prompt"])
        """
        if deploy_name not in self._model_instances:
            raise ValueError(f"Model {deploy_name} not found in pool")

        semaphore = self._semaphores[deploy_name]
        model = self._model_instances[deploy_name]

        async def _use_model():
            async with semaphore:
                return model

        try:
            # 在任务池中执行模型操作
            instance = await self._task_pool.spawn(_use_model())
            yield instance
        finally:
            # 这里可以添加一些清理逻辑，如果需要的话
            pass

    async def refresh_model(self, deploy_name: str):
        """刷新指定模型的实例"""
        async with self._instance_lock:
            if deploy_name not in self._model_instances:
                raise ValueError(f"Model {deploy_name} not found in pool")

            # 获取最新的模型配置
            model = self.model_service.get_by_deploy_name(deploy_name)
            if not model:
                raise ValueError(f"Model {deploy_name} not found in database")

            # 等待当前任务完成
            semaphore = self._semaphores[deploy_name]
            async with semaphore:
                # 更新模型实例
                self._model_instances[deploy_name] = self._create_model_instance(
                    model)
                self._model_configs[deploy_name] = model
                logger.info(f"Refreshed model {deploy_name}")

    def get_pool_status(self) -> List[Dict]:
        """获取所有模型池的状态信息"""
        status = []
        for deploy_name, model in self._model_instances.items():
            config = self._model_configs[deploy_name]
            semaphore = self._semaphores[deploy_name]
            status.append({
                'deploy_name': deploy_name,
                'name': config.name,
                'provider': config.provider,
                'concurrency_limit': self.DEFAULT_POOL_SIZE,
                'available_slots': semaphore._value,  # 当前可用的并发槽
            })
        return status

    async def cleanup(self):
        """清理所有资源"""
        async with self._instance_lock:
            # 等待所有任务完成
            await self._task_pool.join()

            # 清理资源
            self._model_instances.clear()
            self._model_configs.clear()
            self._semaphores.clear()

            # 关闭数据库连接
            self._db.close()

            logger.info("Cleaned up all model pool resources")

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
            model=model.deploy_name,
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
