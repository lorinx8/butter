from datetime import datetime
from typing import List, Optional

from .repositories import ChatHistoryRepository
from .schemas import ChatHistoryCreate, ChatHistoryMessage


class ChatHistoryService:
    def __init__(self, repository: ChatHistoryRepository):
        self.repository = repository

    async def create_chat_history(self, obj_in: ChatHistoryCreate) -> ChatHistoryMessage:
        """Asynchronously save chat history"""
        db_obj = await self.repository.create(obj_in=obj_in)
        return ChatHistoryMessage.model_validate(db_obj)

    async def get_chat_history_before_time(
        self,
        time: datetime,
        limit: int,
        session_id: str
    ) -> List[ChatHistoryMessage]:
        """Query N chat histories before a specific time"""
        histories = await self.repository.get_before_time(
            time=time,
            limit=limit,
            session_id=session_id
        )
        return [ChatHistoryMessage.model_validate(h) for h in histories]
