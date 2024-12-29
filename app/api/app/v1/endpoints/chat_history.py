from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.db_base import get_async_db
from app.core.auth.security import verify_token
from app.core.exceptions.error_code import ErrorCode
from app.core.schemas.response import error_response, success_response
from app.modules.chat_history.repositories import ChatHistoryRepository
from app.modules.chat_history.services import ChatHistoryService
from app.modules.chat_history.schemas import ChatHistoryMessage, ChatHistoryQuery
from datetime import datetime

router = APIRouter()


def get_chat_history_service(db: AsyncSession = Depends(get_async_db)) -> ChatHistoryService:
    return ChatHistoryService(ChatHistoryRepository(db))


@router.post("/chat-histories/query")
async def get_latest_chat_history(
        request: ChatHistoryQuery,
        chat_history_service: ChatHistoryService = Depends(
            get_chat_history_service),
        _: dict = Depends(verify_token)):
    try:
        time = request.latest_datetime or datetime.now()
        lists = await chat_history_service.get_chat_history_before_time(
            time=time,
            limit=request.limit,
            session_id=request.session_id
        )
        return success_response(data=lists)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
