from datetime import datetime
from typing import Optional, List
from enum import Enum
from uuid import UUID
from langgraph.graph import message
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


class ChatHistoryMessage(BaseModel):
    id: UUID
    sender: SenderType
    content: Optional[str] = None
    image_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)  # 使用本地时间

    class Config:
        from_attributes = True


class ChatHistoryQuery(BaseModel):
    """Schema for querying chat history"""
    latest_datetime: Optional[datetime] = None
    limit: int = 20
    session_id: str

    class Config:
        from_attributes = True
