from typing import Optional, List, Dict
import asyncio

from app.core.database.db_base import get_db
from app.core.exceptions.butter_exception import ButterException
from app.core.exceptions.error_code import ErrorCode
from app.core.logging import logger
from app.modules.bot.business.bot_standard import StandardBotConfig, BotStandard
from app.modules.bot.models import Bot
from app.modules.bot.repositories import BotRepository
from app.modules.llm.repositories import ModelRepository
from app.modules.prompt.repositories import PromptRepository


class BotManager:
    _instance: Optional['BotManager'] = None
    _initialized = False
    _lock: asyncio.Lock = asyncio.Lock()
    _bots: Dict[str, BotStandard] = {}


    @classmethod
    async def get_instance(cls) -> 'BotManager':
        """获取BotManager单例"""
        if not cls._instance:
           raise ButterException(ErrorCode.BOT_MANAGER_NOT_INITIALIZED, "BotManager not initialized, call initialize() first")
        return cls._instance


    @classmethod
    async def initialize(cls):
        """初始化所有活跃的机器人, 并加入到机器人池中"""
        if cls._initialized:
            return
        async with cls._lock:
            if not cls._instance:
                logger.info("load all active bots...")
                # 获取所有活跃的机器人配置
                bot_configs = cls._load_all_active_bot_configs()
                # 初始化所有活跃的机器人
                for bot_config in bot_configs:
                    bot = await cls._create_bot(bot_config)
                    if bot:
                        cls._bots[bot_config.bot_code] = bot
                        logger.info(f"load bot {bot_config.bot_code}, name: {bot_config.bot_name}")
                cls._initialized = True


    @classmethod
    def _load_all_active_bot_configs(cls) -> List[StandardBotConfig]:
        """加载所有活跃机器人的配置"""
        configs = []
        db = next(get_db())
        try:
            # 初始化所有仓库和服务
            model_repository = ModelRepository(db)
            prompt_repository = PromptRepository(db)
            bot_repository = BotRepository(db)

            bots = bot_repository.get_all()
            for bot in bots:
                bot_config = cls._create_bot_config_inner(bot, model_repository, prompt_repository)
                if not bot_config:
                    continue
                configs.append(bot_config)
        finally:
            db.close()
        return configs


    @classmethod
    def _load_bot_config(cls, bot_code: str) -> StandardBotConfig:
        db = next(get_db())
        try:
            # 初始化所有仓库和服务
            bot_repository = BotRepository(db)
            model_repository = ModelRepository(db)
            prompt_repository = PromptRepository(db)

            bot = bot_repository.get_by_code(bot_code)
            if not bot:
                raise ButterException(code=ErrorCode.BOT_NOT_FOUND, message=f"Bot {bot_code} not found")
            bot_config = cls._create_bot_config_inner(bot, model_repository, prompt_repository)
            return bot_config
        finally:
            db.close()


    @classmethod
    def _create_bot_config_inner(cls, bot: Bot, model_repository: ModelRepository, prompt_repository: PromptRepository) -> \
    Optional[StandardBotConfig]:
        deploy_name = bot.properties.get('models_deploy_name')
        if not deploy_name:
            logger.warning(f"Bot {bot.code} has no deploy name")
            return None

        model = model_repository.get_by_deploy_name(deploy_name)
        if not model:
            logger.warning(f"Bot {bot.code} has no model with deploy name {deploy_name}")
            return None

        prompt_code = bot.properties.get('models_prompt_code')
        prompt = prompt_repository.get_by_code(prompt_code)
        if not prompt:
            logger.warning(f"Bot {bot.code} has no prompt with code {prompt_code}")
            return None
        prompt_content = prompt.content

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


    @classmethod
    async def _create_bot(cls, bot_config: StandardBotConfig) -> BotStandard:
        """创建机器人"""
        bot_instance = BotStandard(bot_config)
        await bot_instance.initialize()
        return bot_instance


    @classmethod
    async def get_bot(cls, bot_code: str) -> Optional[BotStandard]:
        """获取机器人实例"""
        if bot_code in cls._bots:
            return cls._bots[bot_code]
        else:
            return None

    @classmethod
    async def refresh_bot(cls, bot_code: str):
        """刷新机器人"""
        if not cls._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")

        db = next(get_db())
        try:
            # 初始化所有仓库和服务
            model_repository = ModelRepository(db)
            prompt_repository = PromptRepository(db)
            bot_repository = BotRepository(db)

            bot = bot_repository.get_by_code(bot_code)
            if bot:
                bot_config = cls._create_bot_config_inner(bot, model_repository, prompt_repository)
            else:
                raise ButterException(code=ErrorCode.BOT_NOT_FOUND, message=f"Bot {bot_code} not found")


            bot_instance = await cls._create_bot(bot_config)
            cls._bots[bot_code] = bot_instance

        finally:
            db.close()


    @classmethod
    async def remove_bot(cls, bot_code: str):
        """移除机器人"""
        if not cls._initialized:
            raise RuntimeError("BotManager not initialized. Call initialize() first")

        if bot_code in cls._bots:
            await cls._bots[bot_code].cleanup()
            del cls._bots[bot_code]


    @classmethod
    async def cleanup(cls):
        """清理所有资源"""
        if cls._instance:
            async with cls._lock:
                for bot in cls._bots.values():
                    await bot.cleanup()
                cls._bots.clear()
                cls._initialized = False
                cls._instance = None
                logger.info("BotManager cleaned up successfully")
