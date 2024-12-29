import asyncio
from typing import Optional, Dict

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, AzureChatOpenAI

from app.core.database.db_base import get_db
from app.core.exceptions.butter_exception import ButterException
from app.modules.llm.models import Model
from app.modules.llm.repositories import ModelRepository
from app.core.exceptions.error_code import ErrorCode
from app.core.logging import logger


class ModelManager:
    _instance: Optional['ModelManager'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False
    _models: Dict[str, BaseChatModel] = {}

    @classmethod
    async def get_instance(cls) -> 'ModelManager':
        """获取ModelManager单例实例"""
        if not cls._instance:
            raise ButterException(ErrorCode.MODEL_MANAGER_NOT_INITIALIZED, "ModelManager not initialized, call initialize() first")
        return cls._instance


    @classmethod
    async def initialize(cls):
        if cls._initialized:
            return
        async with cls._lock:
            if not cls._instance:
                logger.info("load all active models...")
                cls._load_all_active_models()
                cls._initialized = True


    @classmethod
    def _load_all_active_models(cls):
        db = next(get_db())
        try:
            # 初始化所有仓库和服务
            model_repository = ModelRepository(db)
            models = model_repository.get_all()
            logger.info(f"find {len(models)} active models...")
            for model in models:
                chat_model = cls._create_model_instance_inner(model)
                if not chat_model:
                    continue
                logger.info(f"load model {model.name}, deploy name: {model.deploy_name}, provider: {model.provider}")
                cls._models[model.deploy_name] = chat_model
        finally:
            db.close()


    @classmethod
    async def refresh_model(cls, deploy_name: str):
        db = next(get_db())
        try:
            # 初始化所有仓库和服务
            model_repository = ModelRepository(db)
            model = model_repository.get_by_deploy_name(deploy_name)
            if not model:
                raise ButterException(ErrorCode.MODEL_NOT_FOUND, "Model not found")
            cls._models[deploy_name] = cls._create_model_instance_inner(model)
        finally:
            db.close()

    @classmethod
    async def get_model(cls, deploy_name: str) -> Optional[BaseChatModel]:
        if not cls._initialized:
            await cls.initialize()
        return cls._models[deploy_name]


    @classmethod
    async def cleanup(cls):
        """清理所有资源"""
        if cls._instance:
            async with cls._lock:
                for model in cls._models.values():
                    await model.close()
                cls._models.clear()
                cls._initialized = False
                cls._instance = None

    # -------------------------------------- -------------------------------------- --------------------
    # -------------------------------------- create model releated -------------------------------------
    @classmethod
    def _create_model_instance_inner(cls, model: Model) -> BaseChatModel:
        """根据模型配置创建新的模型实例"""
        if model.provider == 'openai':
            return cls._create_openai_instance(model)
        elif model.provider == 'azure_openai':
            return cls._create_azure_openai_instance(model)
        raise ValueError(f"Unsupported model provider: {model.provider}")


    @classmethod
    def _create_openai_instance(cls, model: Model) -> BaseChatModel:
        """创建OpenAI模型实例"""
        return ChatOpenAI(
            model=model.properties.get('model'),
            api_key=model.properties.get('api_key'),
            base_url=model.properties.get('base_url'),
        )

    @classmethod
    def _create_azure_openai_instance(cls, model: Model) -> BaseChatModel:
        """创建Azure OpenAI模型实例"""
        return AzureChatOpenAI(
            azure_endpoint=model.properties.get('endpoint'),
            azure_deployment=model.properties.get('deployment_name'),
            openai_api_version=model.properties.get('openai_api_version'),
        )
