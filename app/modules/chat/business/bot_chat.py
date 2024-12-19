from typing import Union, AsyncGenerator, Optional
from app.core.logging import logger
from app.modules.bot.business.bot_manager import BotManager


class BotChat:
    """机器人聊天类,提供通过Bot进行聊天的功能"""

    @staticmethod
    async def chat(bot_code: str, session_id: str, messages: str, image_url: Optional[str] = None, stream: bool = False) -> Union[str, AsyncGenerator]:
        """
        执行机器人聊天
        Args:
            bot_code: 机器人ID
            session_id: 会话ID
            messages: 消息列表
            image_url: 图片URL
            stream: 是否使用流式输出
        Returns:
            非流式模式返回字符串响应,流式模式返回生成器
        """
        if stream:
            return BotChat.chat_stream(bot_code, session_id, messages, image_url)
        return await BotChat.chat_sync(bot_code, session_id, messages, image_url)

    @staticmethod
    async def chat_sync(bot_code: str, session_id: str, messages: str, image_url: Optional[str] = None) -> str:
        """执行同步聊天"""
        try:
            bot_manager = await BotManager.get_instance()
            async with bot_manager.get_bot_instance(bot_code) as bot:
                response = await bot.chat(session_id, messages, image_url)
                return response
        except Exception as e:
            logger.error("Error in bot chat_sync: %s", str(e))
            raise

    @staticmethod
    async def chat_stream(bot_code: str, session_id: str, messages: str, image_url: Optional[str] = None) -> AsyncGenerator[str, None]:
        """执行流式聊天"""
        bot_manager = await BotManager.get_instance()
        async with bot_manager.get_bot_instance(bot_code) as bot:
            async for chunk in bot.chat_stream(session_id, messages, image_url):
                yield chunk
