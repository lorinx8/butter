from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.modules.bot.business.bot_manager import BotManager
from app.modules.chat_history.message_handler import save_chat_message
from app.modules.chat_history.schemas import SenderType
import json


class ChatHistory:
    """聊天历史记录操作类"""
    
    def __init__(self, db: AsyncSession, session_id: str, bot_code: str):
        self.db = db
        self.session_id = session_id
        self.bot_code = bot_code

    async def save_user_message(self, content: str, image_url: Optional[str] = None) -> None:
        """保存用户消息"""
        await save_chat_message(
            db=self.db,
            sender=SenderType.USER,
            session_id=self.session_id,
            content=content,
            bot_code=self.bot_code,
            image_url=image_url
        )

    async def save_ai_message(self, content: str) -> None:
        """保存AI消息"""
        await save_chat_message(
            db=self.db,
            sender=SenderType.AI,
            session_id=self.session_id,
            content=content,
            bot_code=self.bot_code
        )


class BotChat:
    @staticmethod
    async def chat_stream(
        bot_code: str,
        session_id: str,
        messages: str,
        db: AsyncSession,
        image_url: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天
        Args:
            bot_code: 机器人编码
            session_id: 会话ID
            messages: 消息列表
            db: 数据库会话
            image_url: 图片URL
        Returns:
            返回生成器
        """
        try:
            # 初始化聊天历史记录操作
            history = ChatHistory(db, session_id, bot_code)
            
            # 保存用户消息
            await history.save_user_message(messages, image_url)

            # 执行聊天
            async with BotManager.get_bot(bot_code) as bot:
                # 用于收集AI的完整响应
                response_contents = []
                try:
                    async for chunk in bot.chat_stream(session_id, messages, image_url):
                        # 解析JSON获取内容
                        chunk_data = json.loads(chunk)
                        content = chunk_data.get("content", "")
                        
                        # 如果不是结束标记，收集内容
                        if content != "[END]":
                            response_contents.append(content)
                        
                        # 返回原始chunk用于流式输出
                        yield chunk
                    
                    # 所有chunk都返回后，保存完整响应
                    full_response = "".join(response_contents)
                    await history.save_ai_message(full_response)
                except Exception as e:
                    logger.error(f"Error in stream chat: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error in bot chat stream: {str(e)}")
            raise

    @staticmethod
    async def chat(
        bot_code: str,
        session_id: str,
        messages: str,
        db: AsyncSession,
        image_url: Optional[str] = None,
    ) -> str:
        """
        执行机器人聊天
        Args:
            bot_code: 机器人编码
            session_id: 会话ID
            messages: 消息列表
            db: 数据库会话
            image_url: 图片URL
        Returns:
            非流式模式返回字符串响应
        """
 
        try:
            # 初始化聊天历史记录操作
            history = ChatHistory(db, session_id, bot_code)
            
            # 保存用户消息
            await history.save_user_message(messages, image_url)

            # 执行聊天
            async with BotManager.get_bot(bot_code) as bot:
                response = await bot.chat(session_id, messages, image_url)
                
                # 保存AI响应
                await history.save_ai_message(response)
                
                return response
        except Exception as e:
            logger.error(f"Error in bot chat: {str(e)}")
            raise
