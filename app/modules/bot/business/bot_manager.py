from typing import Optional, List, Dict
import asyncio
from fastapi import Depends
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from sqlalchemy.util import b

from app.core.database.db_base import SessionLocal, get_db
from app.core.logging import logger
from app.modules.bot.business.bot_db_pool import BotDatabasePool
from app.modules.bot.business.bot_pool import BotPool
from app.modules.bot.business.bot_standard import StandardBotConfig, BotStandard
from app.modules.bot.models import Bot
from app.modules.bot.repositories import BotRepository
from app.modules.bot.services import BotService
from app.modules.llm.repositories import ModelRepository, ModelProviderRepository
from app.modules.llm.services import ModelService
from app.modules.prompt.repositories import PromptRepository
from app.modules.prompt.services import PromptService


async def _create_bot_config(bot: Bot, model_service: ModelService, prompt_service: PromptService) -> Optional[StandardBotConfig]:
    deploy_name = bot.properties.get('models_deploy_name')
    if not deploy_name:
        logger.warning(f"Bot {bot.code} has no deploy name")
        return None

    model = model_service.get_by_deploy_name(deploy_name)
    if not model:
        logger.warning(f"Bot {bot.code} has no model with deploy name {deploy_name}")
        return None

    prompt_code = bot.properties.get('models_prompt_code')
    prompt_content = prompt_service.get_prompt_content_by_code(prompt_code) or None
    if not prompt_content:
        logger.warning(f"Bot {bot.code} has no prompt with code {prompt_code}, set to None")

    bot_config = StandardBotConfig(
        bot_code=bot.code,
        bot_name=bot.name,
        bot_version=bot.version,
        deploy_name=deploy_name,
        provider_code=model.provider,
        model_properties=model.properties,
        prompt_template=prompt_content,
        memory_enable=bot.properties.get('memory_enable', False),
        memory_strategy=bot.properties.get('memory_strategy'),
        memory_max_tokens=bot.properties.get('max_tokens'),
        memory_max_rounds=bot.properties.get('max_message_rounds'),
    )
    return bot_config


class BotManager:
    _instance: Optional['BotManager'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    def __init__(self):
        """私有初始化方法"""
        self.model_repository = None
        self.model_provider_repository = None
        self.prompt_repository = None
        self.bot_repository = None

        self.model_service = None
        self.prompt_service = None
        self.bot_service = None


    @classmethod
    async def initialize(cls) -> 'BotManager':
        """初始化BotManager单例"""
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls()

                await BotDatabasePool.get_pool()

                pool_instance = await BotPool.initialize()
                db = SessionLocal()

                try:
                    # 初始化所有仓库和服务
                    model_repository = ModelRepository(db)
                    model_provider_repository = ModelProviderRepository(db)
                    prompt_repository = PromptRepository(db)
                    bot_repository = BotRepository(db)

                    model_service = ModelService(model_repository, model_provider_repository)
                    prompt_service = PromptService(prompt_repository)
                    bot_service = BotService(bot_repository)

                    bot_configs = []
                    bots = bot_service.get_all()
                    for bot in bots:
                        bot_config = await _create_bot_config(bot, model_service, prompt_service)
                        if not bot_config:
                            continue
                        bot_configs.append(bot_config)
                    await pool_instance.initialize_pools(bot_configs)
                    
                finally:
                    db.close()
            cls._initialized = True
            return cls._instance


    @classmethod
    async def get_instance(cls, db: Session = Depends(get_db)) -> 'BotManager':
        """获取 BotManager 单例实例"""
        if not cls._initialized:
            raise RuntimeError(
                "BotManager not initialized. Call initialize() first")
        instance = cls._instance
        await instance.handle_request(db)
        return instance


    async def handle_request(self, db: Session):
        """处理HTTP请求时的操作，每个请求都会获得新的数据库会话"""
        # 使用传入的数据库会话创建新的仓库实例
        self.model_repository = ModelRepository(db)
        self.model_provider_repository = ModelProviderRepository(db)
        self.prompt_repository = PromptRepository(db)
        self.bot_repository = BotRepository(db)

        self.model_service = ModelService(self.model_repository, self.model_provider_repository)
        self.prompt_service = PromptService(self.prompt_repository)
        self.bot_service = BotService(self.bot_repository)


    @asynccontextmanager
    async def get_bot_instance(self, bot_code: str):
        """
        获取机器人实例的异步上下文管理器
        """
        pool_instance = await BotPool.get_instance()
        async with pool_instance.get_bot(bot_code) as bot:
            if not bot:
                raise ValueError(f"Bot {bot_code} not found")
            try:
                yield bot
            finally:
                pass


    async def get_pool_status(self) -> List[Dict]:
        """获取机器人池状态"""
        if not self._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")
        pool_instance = await BotPool.get_instance()
        return await pool_instance.get_pool_status()


    async def refresh_bot(self, bot_code: str):
        """刷新机器人"""
        if not self._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")
        pool_instance = await BotPool.get_instance()
        await pool_instance.remove_bot(bot_code)

        bot = self.bot_service.get_bot_by_code(bot_code)
        bot_config = await _create_bot_config(bot, self.model_service, self.prompt_service)
        if not bot_config:
            raise ValueError(f"Bot {bot_code} not found")
        await pool_instance.add_bot(bot_config)


    async def refresh_pool(self):
        """刷新机器人池"""
        if not self._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")

        logger.info("Refreshing bot pool...")
        pool_instance = await BotPool.get_instance()

        # 获取数据库中的所有机器人
        db_bots = {bot.code: bot for bot in self.bot_service.get_bots()}
        pool_bots = pool_instance.config.bot_instances

        # 找出需要删除、添加和更新的机器人
        bots_to_remove = set(pool_bots.keys()) - set(db_bots.keys())
        bots_to_add = set(db_bots.keys()) - set(pool_bots.keys())
        bots_to_update = {
            bot_code for bot_code in set(pool_bots.keys()) & set(db_bots.keys())
            if (db_bots[bot_code].version != pool_bots[bot_code].config.bot_version)
        }

        # 执行更新操作
        for bot_code in bots_to_remove:
            await pool_instance.remove_bot(bot_code)

        for bot_code in bots_to_add | bots_to_update:
            bot = db_bots[bot_code]
            if bot_code in bots_to_update:
                await pool_instance.remove_bot(bot_code)

            bot_config = await _create_bot_config(bot, self.model_service, self.prompt_service)
            await pool_instance.add_bot(bot_config)

        return {
            "removed": len(bots_to_remove),
            "added": len(bots_to_add),
            "updated": len(bots_to_update),
            "total": len(db_bots)
        }


    @asynccontextmanager
    async def get_bot_instance(self, bot_code: str):
        """
        获取机器人实例的异步上下文管理器
        """
        if not self._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")
        pool_instance = await BotPool.get_instance()
        async with pool_instance.get_bot(bot_code) as bot:
            if not bot:
                raise ValueError(f"Bot {bot_code} not found")
            try:
                yield bot
            finally:
                pass


    async def remove_bot(self, bot_code: str):
        """移除机器人"""
        if not self._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")

        pool_instance = await BotPool.get_instance()
        await pool_instance.remove_bot(bot_code)


    @classmethod
    async def cleanup(cls):
        """清理所有资源"""
        if cls._instance:
            await BotDatabasePool.close_pool()
            pool_instance = await BotPool.get_instance()
            if pool_instance:
                await BotPool.cleanup()
            cls._initialized = False
            cls._instance = None
