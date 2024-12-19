from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.sql import func

from app.core.database.models.base import BaseModel
from .schemas import SenderType


class ChatHistory(BaseModel):
    """Chat history model with partitioning by timestamp"""
    __tablename__ = "chat_histories"

    timestamp = Column(DateTime, nullable=False, default=func.now())
    sender = Column(Enum(SenderType), nullable=False)
    session_id = Column(String, nullable=False, index=True)
    content = Column(String, nullable=True)
    bot_code = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
