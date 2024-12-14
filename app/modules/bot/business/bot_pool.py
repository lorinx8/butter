from typing import Dict, Optional, List, Final
import asyncio
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from app.core.logging import logger
from app.modules.bot.business.bot_standard import BotStandard
from app.modules.bot.models import Bot


@dataclass
class BotPoolConfig:
    """BotPool的配置数据类"""
    bot_instances: Dict[str, BotStandard] = field(default_factory=dict)
    bot_configs: Dict[str, Bot] = field(default_factory=dict)
    semaphores: Dict[str, asyncio.Semaphore] = field(default_factory=dict)
    instance_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def get_semaphore_value(self, bot_id: str) -> int:
        """获取信号量的当前值"""
        semaphore = self.semaphores.get(bot_id)
        if semaphore is None:
            return 0
        # 信号量的_value属性表示当前可用的槽位数
        return semaphore._value


class BotPool:
    """机器人池管理类"""

    DEFAULT_POOL_SIZE: Final = 3
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

    def get_bot_instance(self, bot_id: str) -> Optional[BotStandard]:
        """获取机器人实例"""
        return self._config.bot_instances.get(bot_id)

    def get_bot_config(self, bot_id: str) -> Optional[Bot]:
        """获取机器人配置"""
        return self._config.bot_configs.get(bot_id)

    def has_bot(self, bot_id: str) -> bool:
        """检查机器人是否在池中"""
        return bot_id in self._config.bot_instances

    async def get_semaphore(self, bot_id: str) -> Optional[asyncio.Semaphore]:
        """获取机器人的信号量"""
        return self._config.semaphores.get(bot_id)

    @asynccontextmanager
    async def get_bot(self, bot_id: str):
        """获取机器人实例的上下文管理器"""
        if not self.has_bot(bot_id):
            raise ValueError(f"Bot {bot_id} not found in pool")

        semaphore = await self.get_semaphore(bot_id)
        bot = self.get_bot_instance(bot_id)

        try:
            async with semaphore:
                yield bot
        finally:
            pass

    async def add_bot(self, bot_id: str, bot_config: Bot, bot_instance: BotStandard):
        """添加机器人到池中"""
        async with self._config.instance_lock:
            if not self.has_bot(bot_id):
                self._config.bot_instances[bot_id] = bot_instance
                self._config.bot_configs[bot_id] = bot_config
                self._config.semaphores[bot_id] = asyncio.Semaphore(
                    self.DEFAULT_POOL_SIZE)
                logger.info(f"Added bot to pool: {bot_id}")

    async def remove_bot(self, bot_id: str):
        """从池中移除机器人"""
        async with self._config.instance_lock:
            if self.has_bot(bot_id):
                semaphore = await self.get_semaphore(bot_id)
                async with semaphore:
                    self._config.bot_instances.pop(bot_id)
                    self._config.bot_configs.pop(bot_id)
                    self._config.semaphores.pop(bot_id)
                    logger.info(f"Removed bot from pool: {bot_id}")

    async def get_pool_status(self) -> List[Dict]:
        """获取所有机器人池的状态信息"""
        status = []
        for bot_id in self._config.bot_instances.keys():
            config = self.get_bot_config(bot_id)
            available_slots = await self._config.get_semaphore_value(bot_id)
            status.append({
                'bot_id': bot_id,
                'name': config.name,
                'type': config.bot_type,
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
                instance_config.bot_configs.clear()
                instance_config.semaphores.clear()
                logger.info("Cleaned up all bot pool resources")
                cls._initialized = False
                cls._instance = None
