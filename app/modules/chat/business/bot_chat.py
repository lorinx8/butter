from typing import Union, AsyncGenerator
from app.core.logging import logger
from app.modules.bot.business.bot_manager import BotManager


class BotChat:
    """机器人聊天类,提供通过Bot进行聊天的功能"""

    @staticmethod
    async def chat(bot_id: str, session_id: str, messages: str, stream: bool = False) -> Union[str, AsyncGenerator]:
        """
        执行机器人聊天
        Args:
            bot_id: 机器人ID
            session_id: 会话ID
            messages: 消息列表
            stream: 是否使用流式输出
        Returns:
            非流式模式返回字符串响应,流式模式返回生成器
        """
        if stream:
            return BotChat.chat_stream(bot_id, session_id, messages)
        return await BotChat.chat_sync(bot_id, session_id, messages)

    @staticmethod
    async def chat_sync(bot_id: str, session_id: str, messages: str) -> str:
        """执行同步聊天"""
        try:
            bot_manager = await BotManager.get_instance()
            async with bot_manager.get_bot_instance(bot_id) as bot:
                response = await bot.chat(session_id, messages)
                return response
        except Exception as e:
            logger.error("Error in bot chat_sync: %s", str(e))
            raise

    @staticmethod
    async def chat_stream(bot_id: str, session_id: str, messages: str) -> AsyncGenerator[str, None]:
        """执行流式聊天"""
        bot_manager = await BotManager.get_instance()
        async with bot_manager.get_bot_instance(bot_id) as bot:
            async for chunk in bot.chat_stream(session_id, messages):
                yield chunk
