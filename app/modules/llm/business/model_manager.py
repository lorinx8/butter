import asyncio
from typing import Optional, Dict, List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database.db_base import get_db, SessionLocal
from app.core.exceptions.butter_exception import ButterException
from app.modules.llm.repositories import ModelRepository, ModelProviderRepository
from app.modules.llm.services import ModelService
from app.modules.llm.business.model_pool import ModelPool
from app.core.schemas.error_code import ErrorCode

class ModelManager:
    _instance : Optional['ModelManager'] = None
    _lock : asyncio.Lock = asyncio.Lock()
    _initialized : bool = False

    def __init__(self):
        self.model_repository = None
        self.model_service = None
        self.provider_repository = None

    @classmethod
    async def initialize(cls) -> 'ModelManager':
        async with (cls._lock):
            if not cls._instance:
                cls._instance = cls()
                
            await ModelPool.initialize()
            db = SessionLocal()

            try:
                model_repository = ModelRepository(db)
                model_provider_repository = ModelProviderRepository(db)
                model_service = ModelService(
                    model_repository, model_provider_repository)

                # get all active models
                active_models = model_service.get_active_models()
                instance = await ModelPool.get_instance()
                await instance.initialize_pools(active_models)
            finally:
                db.close()
                
            cls._initialized = True
            return cls._instance


    @classmethod
    async def get_instance(cls, db: Session = Depends(get_db)) -> 'ModelManager':
        if not cls._initialized:
            raise RuntimeError(
                "ModelManager not initialized. Call initialize() first")
        instance = cls._instance
        await instance.handle_request(db)
        return instance


    async def handle_request(self, db: Session):
        """处理HTTP请求时的操作，每个请求都会获得新的数据库会话"""
        # 使用传入的数据库会话创建新的仓库实例
        self.model_repository = ModelRepository(db)
        self.provider_repository = ModelProviderRepository(db)
        self.model_service = ModelService(
            self.model_repository,
            self.provider_repository
        )


    async def refresh_model(self, deploy_name: str) -> str:
        model = self.model_service.get_by_deploy_name(deploy_name)
        if not model:
            raise ButterException(ErrorCode.MODEL_NOT_FOUND, "Model not found")
        instance = await ModelPool.get_instance()
        return await instance.refresh_model(deploy_name, model)


    async def refresh_pool(self) -> Dict[str, List[str]]:
        active_models = self.model_service.get_active_models()
        instance = await ModelPool.get_instance()
        return await instance.refresh_pool(active_models)


    @classmethod
    async def get_pool_status(cls):
        instance = await ModelPool.get_instance()
        return await instance.get_pool_status()