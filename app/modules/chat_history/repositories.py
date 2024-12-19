from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ChatHistory
from .schemas import ChatHistoryCreate


class ChatHistoryRepository():
    """Repository for chat history operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, *, obj_in: ChatHistoryCreate) -> ChatHistory:
        db_obj = ChatHistory(
            timestamp=obj_in.timestamp,
            sender=obj_in.sender,
            session_id=obj_in.session_id,
            content=obj_in.content,
            bot_code=obj_in.bot_code,
            image_url=obj_in.image_url
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_by_time_range(
        self,
        *,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        session_id: Optional[str] = None
    ) -> List[ChatHistory]:
        query = select(ChatHistory)
        
        if start_time:
            query = query.where(ChatHistory.timestamp >= start_time)
        if end_time:
            query = query.where(ChatHistory.timestamp <= end_time)
        if session_id:
            query = query.where(ChatHistory.session_id == session_id)
            
        query = query.order_by(desc(ChatHistory.timestamp))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_before_time(
        self,
        *,
        time: datetime,
        limit: int,
        session_id: Optional[str] = None
    ) -> List[ChatHistory]:
        query = select(ChatHistory).where(ChatHistory.timestamp <= time)
        
        if session_id:
            query = query.where(ChatHistory.session_id == session_id)
            
        query = query.order_by(desc(ChatHistory.timestamp)).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
