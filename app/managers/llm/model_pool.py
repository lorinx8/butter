"""
LangChain model pool manager.
This module provides a pool manager for LangChain models, handling the lifecycle
and concurrent access of model instances.
"""

from typing import Dict, Optional, List, Final
import asyncio
from asyncio_pool import AioPool
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from app.services.model_service import ModelService
from app.repositories.model_repository import ModelRepository
from app.repositories.model_provider_repository import ModelProviderRepository
from app.repositories.models import Model
from app.core.logging import logger
from app.core.database import SessionLocal


class ModelPool:
    """LangChain模型池管理类，负责维护和管理所有模型实例"""

    DEFAULT_POOL_SIZE: Final = 3
    _instance: Optional['ModelPool'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    def __init__(self):
        """
        初始化方法是私有的，请使用 get_instance() 或 initialize() 方法获取实例
        """
        # 初始化服务和依赖
        db = SessionLocal()
        self.model_repository = ModelRepository(db)
        self.provider_repository = ModelProviderRepository(db)
        self.model_service = ModelService(
            self.model_repository, self.provider_repository)

        # key: 模型的唯一标识符（model.deploy_name） value: 用于控制该模型并发访问的池对象
        self._model_pools: Dict[str, AioPool] = {}

        # key: 模型的唯一标识符（model.deploy_name） value: 该模型的实例
        self._model_instances: Dict[str, None | BaseChatModel] = {}

        # key: 模型的唯一标识符（model.deploy_name） value: 该模型的配置信息
        self._model_configs: Dict[str, Model] = {}

        self._instance_lock = asyncio.Lock()

    @classmethod
    async def initialize(cls) -> 'ModelPool':
        """
        初始化ModelPool单例

        Returns:
            ModelPool: 初始化后的ModelPool实例
        """
        # 初始化模型池
        logger.info("开始初始化模型池...")
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls()
                cls._initialized = True
                # 初始化模型池
                await cls._instance._initialize_pools()
            return cls._instance

    @classmethod
    async def get_instance(cls) -> 'ModelPool':
        """
        获取ModelPool单例实例

        Returns:
            ModelPool: ModelPool单例实例

        Raises:
            RuntimeError: 如果ModelPool未初始化
        """
        if not cls._initialized:
            raise RuntimeError(
                "ModelPool not initialized. Call initialize() first")
        return cls._instance

    async def _initialize_pools(self):
        """初始化所有模型池"""
        async with self._instance_lock:
            active_models = self.model_service.get_active_models()
            logger.info(f"开始初始化模型池，发现 {len(active_models)} 个活跃模型")
            for model in active_models:
                await self._initialize_model_pool(model)
            logger.info("模型池初始化完成")

    async def _initialize_model_pool(self, model: Model):
        """初始化单个模型的模型池"""
        if model.deploy_name in self._model_pools:
            logger.info(f"模型 {model.deploy_name} 已存在于模型池中，跳过初始化")
            return

        try:
            # 创建模型实例
            logger.info(f"正在初始化模型 {model.deploy_name}（{model.provider}）")
            instance = self._create_model_instance(model)

            # 创建并发控制池
            pool = AioPool(size=self.DEFAULT_POOL_SIZE)

            self._model_pools[model.deploy_name] = pool
            self._model_instances[model.deploy_name] = instance
            self._model_configs[model.deploy_name] = model

            logger.info(
                f"模型 {model.deploy_name} 初始化成功，并发池大小：{self.DEFAULT_POOL_SIZE}")
        except Exception as e:
            logger.error(f"模型 {model.deploy_name} 初始化失败：{str(e)}")
            raise

    async def get_model(self, model_code: str) -> Optional[BaseChatModel]:
        """从模型池中获取一个模型实例并执行任务"""
        if model_code not in self._model_pools:
            raise ValueError(f"Model {model_code} not found in pool")

        pool = self._model_pools[model_code]
        model = self._model_instances[model_code]

        # 使用 AioPool 来控制并发
        async def _get_model():
            return model

        # 在并发池中执行获取模型的操作
        return await pool.spawn(_get_model())

    async def refresh_model(self, deploy_name: str):
        """刷新指定模型的实例"""
        async with self._instance_lock:
            if deploy_name not in self._model_pools:
                raise ValueError(f"Model {deploy_name} not found in pool")

            # 获取最新的模型配置
            model = self.model_service.get_by_deploy_name(deploy_name)
            if not model:
                raise ValueError(f"Model {deploy_name} not found in database")

            # 清理现有实例
            self._model_instances[deploy_name] = None

            # 重新初始化池
            await self._initialize_model_pool(model)
            logger.info(f"Refreshed model pool for {deploy_name}")

    def get_pool_status(self) -> List[Dict]:
        """获取所有模型池的状态信息"""
        status = []
        for model_code, pool in self._model_pools.items():
            model_config = self._model_configs[model_code]
            status.append({
                'deploy_name': model_code,
                'name': model_config.name,
                'provider': model_config.provider,
            })
        return status

    @classmethod
    async def cleanup(cls):
        """清理模型池资源的类方法"""
        instance = await cls.get_instance()
        logger.info("开始清理模型池资源...")
        # 执行实际的清理工作
        await instance._cleanup()
        logger.info("模型池资源清理完成")

    async def _cleanup(self):
        """实际的清理工作"""
        for deploy_name, pool in self._model_pools.items():
            logger.info(f"正在清理模型 {deploy_name} 的资源")
            # 清空模型池
            self._model_pools[deploy_name] = None
            self._model_instances[deploy_name] = None
            self._model_configs[deploy_name] = None

        # 清空所有字典
        self._model_pools.clear()
        self._model_instances.clear()
        self._model_configs.clear()

    # --------------------------------------------------------------------------
    # 模型实例创建
    # --------------------------------------------------------------------------

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
