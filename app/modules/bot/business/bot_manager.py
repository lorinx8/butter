from typing import Dict, Optional
import asyncio
from fastapi import HTTPException

from app.core.database.db_base import SessionLocal
from app.core.logging import logger
from app.modules.bot.business.bot_pool import BotPool
from app.modules.bot.business.bot_standard import BotConfig, BotStandard
from app.modules.bot.repositories import BotRepository
from app.modules.bot.schemas import BotStandardCreate
from app.modules.bot.services import BotService
from app.modules.llm.repositories import ModelRepository, ModelProviderRepository
from app.modules.llm.services import ModelService
from app.modules.prompt.repositories import PromptRepository
from app.modules.prompt.services import PromptService


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
                # 把已有的机器人放到池里
                await cls._instance.load_bots_to_pool()
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
    # 获取智能体信息，并添加到池中
    # ------------------------------------------------------------

    async def load_bots_to_pool(self):
        """从数据库加载所有机器人并添加到池中"""

        if not self._initialized:
            raise RuntimeError(
                "BotManager not initialized. Call initialize() first")

        logger.info("Loading bots to pool...")
        # 获取所有机器人
        bots = self.bot_service.get_bots()
        if not bots or len(bots) == 0:
            logger.info("No bots found")
            return
        else:
            logger.info(f"Found {len(bots)} bots")

        '''
        properties:
        {
            "max_tokens": 333,
            "memory_enable": true,
            "memory_strategy": "tokens",
            "max_message_rounds": null,
            "models_deploy_name": "openai-gpt-4o",
            "models_prompt_code": "prompt-20241126174648-EqSH"
        }
        '''
        for bot in bots:
            logger.info(f"Loading bot: {bot.code} - {bot.name}")
            # 通过部署名得到提供商的真实模型名
            deploy_name = bot.properties.get('models_deploy_name')
            if deploy_name is None:
                logger.warning(f"Bot {bot.code} has no deploy name")
                continue
            model = self.model_service.get_by_deploy_name(deploy_name)
            if not model:
                logger.warning(f"Bot {bot.code} has no model")
                continue
            # 得到提示词内容
            prompt_code = bot.properties.get('models_prompt_code')
            prompt_content = self.prompt_service.get_prompt_content_by_code(
                prompt_code)
            # 检查是否存在
            if not prompt_content:
                prompt_content = ''

            # 创建 BotConfig 实例
            bot_config = BotConfig(
                bot_code=bot.code,
                bot_name=bot.name,
                deploy_name=deploy_name,
                provider_code=model.provider,
                model_properties=model.properties,
                prompt_template=prompt_content,

                memory_enable=bot.properties.get('memory_enable', False),
                memory_strategy=bot.properties.get('memory_strategy'),
                memory_max_tokens=bot.properties.get('max_tokens'),
                memory_max_rounds=bot.properties.get('max_message_rounds'),
            )

            # 创建 BotStandard 实例
            bot_instance = BotStandard(bot_config)

            # 将机器人添加到池中
            await self.bot_pool.add_bot(bot.id, bot, bot_instance)

        logger.info(f"Loaded {len(bots)} bots into the pool")

    # ------------------------------------------------------------
    # 添加标准机器人
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

    async def get_bot_instance(self, bot_id: str) -> BotStandard:
        """获取机器人实例"""
        return await self.bot_pool.get_bot(bot_id)

    async def remove_bot(self, bot_id: str):
        """移除机器人"""
        await self.bot_pool.remove_bot(bot_id)

    async def refresh_pool(self):
        """
        刷新机器人池
        - 同步数据库中的机器人到机器人池
        - 添加新机器人，移除已删除机器人
        - 更新配置已改变的机器人
        """
        if not self._initialized:
            raise RuntimeError(
                "BotManager not initialized. Call initialize() first")

        logger.info("Refreshing bot pool...")

        # 获取数据库中的所有机器人
        db_bots = {bot.id: bot for bot in self.bot_service.get_bots()}

        # 获取当前池中的所有机器人
        pool_bots = self.bot_pool._config.bot_configs

        # 找出需要删除的机器人（在池中但不在数据库中）
        bots_to_remove = set(pool_bots.keys()) - set(db_bots.keys())

        # 找出需要添加的机器人（在数据库中但不在池中）
        bots_to_add = set(db_bots.keys()) - set(pool_bots.keys())

        # 找出需要更新的机器人（配置发生变化）
        bots_to_update = set()
        for bot_id in set(pool_bots.keys()) & set(db_bots.keys()):
            db_bot = db_bots[bot_id]
            pool_bot = pool_bots[bot_id]

            # 检查配置是否发生变化
            if (db_bot.properties != pool_bot.properties or
                db_bot.name != pool_bot.name or
                    db_bot.code != pool_bot.code):
                bots_to_update.add(bot_id)

        # 1. 移除已删除的机器人
        for bot_id in bots_to_remove:
            logger.info(f"Removing bot from pool: {bot_id}")
            await self.bot_pool.remove_bot(bot_id)

        # 2. 添加新机器人
        for bot_id in bots_to_add:
            bot = db_bots[bot_id]
            logger.info(f"Adding new bot to pool: {bot.code} - {bot.name}")

            # 获取模型和提示词配置
            deploy_name = bot.properties.get('models_deploy_name')
            if not deploy_name:
                logger.warning(f"Bot {bot.code} has no deploy name")
                continue

            model = self.model_service.get_by_deploy_name(deploy_name)
            if not model:
                logger.warning(f"Bot {bot.code} has no model")
                continue

            prompt_code = bot.properties.get('models_prompt_code')
            prompt_content = self.prompt_service.get_prompt_content_by_code(
                prompt_code) or ''

            # 创建配置和实例
            bot_config = BotConfig(
                bot_code=bot.code,
                bot_name=bot.name,
                deploy_name=deploy_name,
                provider_code=model.provider,
                model_properties=model.properties,
                prompt_template=prompt_content,
                memory_enable=bot.properties.get('memory_enable', False),
                memory_strategy=bot.properties.get('memory_strategy'),
                memory_max_tokens=bot.properties.get('max_tokens'),
                memory_max_rounds=bot.properties.get('max_message_rounds'),
            )
            bot_instance = BotStandard(bot_config)
            await self.bot_pool.add_bot(bot.id, bot, bot_instance)

        # 3. 更新配置已改变的机器人
        for bot_id in bots_to_update:
            logger.info(f"Updating bot in pool: {bot_id}")
            # 先移除旧的实例
            await self.bot_pool.remove_bot(bot_id)
            # 然后添加新的实例
            bot = db_bots[bot_id]
            deploy_name = bot.properties.get('models_deploy_name')
            if not deploy_name:
                logger.warning(f"Bot {bot.code} has no deploy name")
                continue

            model = self.model_service.get_by_deploy_name(deploy_name)
            if not model:
                logger.warning(f"Bot {bot.code} has no model")
                continue

            prompt_code = bot.properties.get('models_prompt_code')
            prompt_content = self.prompt_service.get_prompt_content_by_code(
                prompt_code) or ''

            bot_config = BotConfig(
                bot_code=bot.code,
                bot_name=bot.name,
                deploy_name=deploy_name,
                provider_code=model.provider,
                model_properties=model.properties,
                prompt_template=prompt_content,
                memory_enable=bot.properties.get('memory_enable', False),
                memory_strategy=bot.properties.get('memory_strategy'),
                memory_max_tokens=bot.properties.get('max_tokens'),
                memory_max_rounds=bot.properties.get('max_message_rounds'),
            )
            bot_instance = BotStandard(bot_config)
            await self.bot_pool.add_bot(bot.id, bot, bot_instance)

        logger.info(
            f"Bot pool refresh completed. Removed: {len(bots_to_remove)}, Added: {len(bots_to_add)}, Updated: {len(bots_to_update)}")

        return {
            "removed": len(bots_to_remove),
            "added": len(bots_to_add),
            "updated": len(bots_to_update),
            "total": len(db_bots)
        }

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
