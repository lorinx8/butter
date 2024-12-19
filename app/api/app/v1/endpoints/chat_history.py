from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db_base import get_async_db
from app.modules.chat_history.repositories import ChatHistoryRepository
from app.modules.chat_history.services import ChatHistoryService
from app.modules.chat_history.schemas import ChatHistoryResponse, ChatHistoryQuery

router = APIRouter()


def get_chat_history_service(db: AsyncSession = Depends(get_async_db)) -> ChatHistoryService:
    return ChatHistoryService(ChatHistoryRepository(db))


@router.post("/chat-history/query", response_model=List[ChatHistoryResponse])
async def query_chat_history(
    query: ChatHistoryQuery,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> List[ChatHistoryResponse]:
    """Query chat history by time range"""
    return await chat_history_service.get_chat_history_by_time_range(
        start_time=query.start_time,
        end_time=query.end_time,
        session_id=query.session_id
    )


@router.get("/chat-history/before/{timestamp}", response_model=List[ChatHistoryResponse])
async def get_chat_history_before(
    timestamp: str,
    limit: int = 10,
    session_id: str = None,
    chat_history_service: ChatHistoryService = Depends(get_chat_history_service)
) -> List[ChatHistoryResponse]:
    """Get N chat histories before a specific time"""
    from datetime import datetime
    time = datetime.fromisoformat(timestamp)
    return await chat_history_service.get_chat_history_before_time(
        time=time,
        limit=limit,
        session_id=session_id
    )
