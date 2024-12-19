from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class SenderType(str, Enum):
    USER = "USER"
    AI = "AI"


class ChatHistoryCreate(BaseModel):
    """Schema for creating a chat history record"""
    timestamp: datetime = Field(default_factory=datetime.now)  # 使用本地时间
    sender: SenderType
    session_id: str
    content: Optional[str] = None
    bot_code: str
    image_url: Optional[str] = None


class ChatHistoryResponse(ChatHistoryCreate):
    """Schema for chat history response"""
    id: UUID  # 修改为 UUID 类型

    class Config:
        from_attributes = True


class ChatHistoryQuery(BaseModel):
    """Schema for querying chat history"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: Optional[int] = None
    session_id: Optional[str] = None
