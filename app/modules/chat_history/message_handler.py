from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chat_history.services import ChatHistoryService
from app.modules.chat_history.repositories import ChatHistoryRepository
from app.modules.chat_history.schemas import ChatHistoryCreate, SenderType


async def save_chat_message(
    db: AsyncSession,
    sender: str,
    session_id: str,
    content: str,
    bot_code: str,
    image_url: Optional[str] = None
):
    """异步保存聊天消息"""
    chat_history_service = ChatHistoryService(ChatHistoryRepository(db))
    message = ChatHistoryCreate(
        sender=SenderType(sender),
        session_id=session_id,
        content=content,
        bot_code=bot_code,
        image_url=image_url
    )
    await chat_history_service.create_chat_history(message)
