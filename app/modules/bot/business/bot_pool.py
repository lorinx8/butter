from typing import Dict, Optional, List, Final
import asyncio
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from app.core.logging import logger
from app.modules.bot.business.bot_standard import StandardBotConfig, BotStandard


async def _initialize_standard_bot(bot: StandardBotConfig) -> BotStandard:
    bot_instance = BotStandard(bot)
    await bot_instance.initialize()
    return bot_instance


@dataclass
class BotPoolConfig:
    """BotPool的配置数据类"""
    bot_instances: Dict[str, BotStandard] = field(default_factory=dict)
    semaphores: Dict[str, asyncio.Semaphore] = field(default_factory=dict)
    instance_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def get_semaphore_value(self, bot_code: str) -> int:
        """获取信号量的当前值"""
        semaphore = self.semaphores.get(bot_code)
        if semaphore is None:
            return 0
        # 信号量的_value属性表示当前可用的槽位数
        return semaphore._value


class BotPool:
    """机器人池管理类"""

    DEFAULT_POOL_SIZE: Final = 10
    _instance: Optional['BotPool'] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _initialized: bool = False

    def __init__(self):
        self._config = BotPoolConfig()

    @classmethod
    async def initialize(cls) -> 'BotPool':
        """初始化BotPool单例"""
        async with cls._lock:
            if not cls._instance:
                cls._instance = cls()
                cls._initialized = True
            return cls._instance


    async def initialize_pools(self, bot_configs: Optional[List[StandardBotConfig]] = None):
        for bot_config in bot_configs or []:
            logger.info(f"Loading bot: {bot_config.bot_code} - {bot_config.bot_name}")
            await self.add_bot(bot_config)


    @classmethod
    async def get_instance(cls) -> 'BotPool':
        """获取BotPool单例实例"""
        if not cls._initialized:
            raise RuntimeError(
                "BotPool not initialized. Call initialize() first")
        return cls._instance


    def get_config(self) -> BotPoolConfig:
        """获取机器人池配置"""
        return self._config


    def get_bot_instance(self, bot_code: str) -> Optional[BotStandard]:
        """获取机器人实例"""
        return self._config.bot_instances.get(bot_code)


    def has_bot(self, bot_code: str) -> bool:
        """检查机器人是否在池中"""
        return bot_code in self._config.bot_instances


    async def get_semaphore(self, bot_code: str) -> Optional[asyncio.Semaphore]:
        """获取机器人的信号量"""
        return self._config.semaphores.get(bot_code)


    @asynccontextmanager
    async def get_bot(self, bot_code: str):
        """获取机器人实例的上下文管理器"""
        if not self.has_bot(bot_code):
            raise ValueError(f"Bot {bot_code} not found in pool")

        semaphore = await self.get_semaphore(bot_code)
        bot = self.get_bot_instance(bot_code)

        try:
            async with semaphore:
                yield bot
        finally:
            pass


    async def add_bot(self, bot_config: StandardBotConfig):
        """添加机器人到池中"""
        async with self._config.instance_lock:
            bot_code = bot_config.bot_code
            if not self.has_bot(bot_code):
                bot_instance = await _initialize_standard_bot(bot_config)
                self._config.bot_instances[bot_code] = bot_instance
                self._config.semaphores[bot_code] = asyncio.Semaphore(
                    self.DEFAULT_POOL_SIZE)
                logger.info(f"Added bot to pool: {bot_code}")


    async def remove_bot(self, bot_code: str):
        """从池中移除机器人"""
        async with self._config.instance_lock:
            if self.has_bot(bot_code):
                semaphore = await self.get_semaphore(bot_code)
                async with semaphore:
                    # 获取机器人实例并清理
                    bot_instance = self._config.bot_instances.get(bot_code)
                    if bot_instance:
                        await bot_instance.cleanup()

                    # 从池中移除
                    self._config.bot_instances.pop(bot_code)
                    self._config.semaphores.pop(bot_code)
                    logger.info(f"Removed bot from pool: {bot_code}")


    async def get_pool_status(self) -> List[Dict]:
        """获取所有机器人池的状态信息"""
        status = []
        for bot_code in self._config.bot_instances.keys():
            bot_instance = self._config.bot_instances.get(bot_code)
            available_slots = await self._config.get_semaphore_value(bot_code)
            status.append({
                'bot_code': bot_code,
                'bot_name': bot_instance.bot_name,
                'bot_config': bot_instance.config,
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
                instance_config.bot_instances.clear()
                instance_config.semaphores.clear()
                logger.info("Cleaned up all bot pool resources")
                cls._initialized = False
                cls._instance = None

    @property
    def config(self):
        return self._config
