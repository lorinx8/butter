from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db_base import get_async_db
from app.core.auth.security import verify_token
from app.modules.chat_history.repositories import ChatHistoryRepository
from app.modules.chat_history.services import ChatHistoryService
from app.modules.chat_history.schemas import ChatHistoryMessage, ChatHistoryQuery
from datetime import datetime

router = APIRouter()


def get_chat_history_service(db: AsyncSession = Depends(get_async_db)) -> ChatHistoryService:
    return ChatHistoryService(ChatHistoryRepository(db))


# 改成 POST
@router.post("/chat-histories/query", response_model=List[ChatHistoryMessage])
async def get_latest_chat_history(
    request: ChatHistoryQuery,
    chat_history_service: ChatHistoryService = Depends(
        get_chat_history_service),
    _: dict = Depends(verify_token),
) -> List[ChatHistoryMessage]:
    time = request.latest_datetime or datetime.now()
    return await chat_history_service.get_chat_history_before_time(
        time=time,
        limit=request.limit,
        session_id=request.session_id
    )
