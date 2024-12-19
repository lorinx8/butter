from datetime import datetime
from typing import List, Optional

from .repositories import ChatHistoryRepository
from .schemas import ChatHistoryCreate, ChatHistoryResponse


class ChatHistoryService:
    def __init__(self, repository: ChatHistoryRepository):
        self.repository = repository

    async def create_chat_history(self, obj_in: ChatHistoryCreate) -> ChatHistoryResponse:
        """Asynchronously save chat history"""
        db_obj = await self.repository.create(obj_in=obj_in)
        return ChatHistoryResponse.model_validate(db_obj)

    async def get_chat_history_by_time_range(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        session_id: Optional[str] = None
    ) -> List[ChatHistoryResponse]:
        """Query chat history within a time range"""
        histories = await self.repository.get_by_time_range(
            start_time=start_time,
            end_time=end_time,
            session_id=session_id
        )
        return [ChatHistoryResponse.model_validate(h) for h in histories]

    async def get_chat_history_before_time(
        self,
        time: datetime,
        limit: int,
        session_id: Optional[str] = None
    ) -> List[ChatHistoryResponse]:
        """Query N chat histories before a specific time"""
        histories = await self.repository.get_before_time(
            time=time,
            limit=limit,
            session_id=session_id
        )
        return [ChatHistoryResponse.model_validate(h) for h in histories]
