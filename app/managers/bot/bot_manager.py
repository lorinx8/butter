from typing import Dict, Optional
import asyncio
from fastapi import HTTPException
from app.repositories.model_repository import ModelRepository
from app.repositories.prompt_repository import PromptRepository
from app.repositories.bot_repository import BotRepository
from app.repositories.model_provider_repository import ModelProviderRepository
from app.services.bot_service import BotService
from app.services.model_service import ModelService
from app.services.prompt_service import PromptService
from app.schemas.bot import BotStandardCreate
from app.managers.bot.bot_pool import BotPool
from app.core.database import SessionLocal


class BotManager:
    _instance: Optional['BotManager'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    def __init__(self):
        """私有初始化方法"""
        self.db = SessionLocal()

        self.model_service = ModelService(ModelRepository(
            self.db), ModelProviderRepository(self.db))
        self.prompt_service = PromptService(PromptRepository(self.db))
        self.bot_service = BotService(BotRepository(self.db))

        self.bot_pool = None

    @classmethod
    async def initialize(cls) -> 'BotManager':
        """初始化 BotManager 单例"""
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls()
                # 初始化池
                await cls._instance._init_pools()
                cls._initialized = True
            return cls._instance

    @classmethod
    async def get_instance(cls) -> 'BotManager':
        """获取 BotManager 单例实例"""
        if not cls._initialized:
            raise RuntimeError(
                "BotManager not initialized. Call initialize() first")
        return cls._instance

    async def _init_pools(self):
        """初始化池"""
        if not self.bot_pool:
            self.bot_pool = await BotPool.initialize()

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'db'):
            self.db.close()

    # ------------------------------------------------------------
    # 标准机器人
    # ------------------------------------------------------------
    def create_standard_bot(self, bot_data: BotStandardCreate) -> Dict:
        """
        创建标准机器人
        - 验证机器人类型
        - 验证模型部署是否存在且可用
        - 验证提示词是否存在
        - 创建机器人记录
        """
        # 验证机器人类型
        if bot_data.bot_type != "standard":
            raise HTTPException(
                status_code=400,
                detail="Invalid bot type, must be 'standard'"
            )

        # 验证模型部署
        model_name = bot_data.properties.models_deploy_name
        if not self._validate_model(model_name):
            raise HTTPException(
                status_code=400,
                detail=f"Model deployment '{model_name}' not found or inactive"
            )

        # 验证提示词
        prompt_code = bot_data.properties.models_prompt_code
        if not self._validate_prompt(prompt_code):
            raise HTTPException(
                status_code=400,
                detail=f"Prompt '{prompt_code}' not found"
            )

        bot = self.bot_service.create_bot(bot_data)
        return bot

    def _validate_model(self, deploy_name: str) -> bool:
        """验证模型部署是否存在且可用"""
        model = self.model_service.get_by_deploy_name(deploy_name)
        return model is not None and model.is_active

    def _validate_prompt(self, prompt_code: str) -> bool:
        """验证提示词是否存在"""
        prompt = self.prompt_service.get_prompt_by_code(prompt_code)
        return prompt is not None

    async def chat(self, bot_id: str, session_id: str, message: str, stream: bool = False):
        """处理聊天请求"""
        await self._init_pools()

        async with self.bot_pool.get_bot(bot_id) as bot:
            if stream:
                return await bot.chat_stream(session_id, message)
            else:
                return await bot.chat(session_id, message)

    async def remove_bot(self, bot_id: str):
        """移除机器人"""
        await self._init_pools()
        await self.bot_pool.remove_bot(bot_id)

    @classmethod
    async def cleanup(cls):
        """清理所有资源"""
        if cls._instance:
            # 清理机器人池
            if cls._instance.bot_pool:
                await BotPool.cleanup()

            # 关闭数据库连接
            if hasattr(cls._instance, 'db'):
                cls._instance.db.close()

            # 重置实例
            cls._initialized = False
            cls._instance = None
