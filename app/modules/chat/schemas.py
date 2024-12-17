from typing import List, Dict
from pydantic import BaseModel


class ModelChatRequest(BaseModel):
    """Admin chat request schema"""
    model: str
    messages: List[Dict[str, str]]
    stream: bool = False


class BotChatRequest(BaseModel):
    """Bot chat request schema"""
    bot_code: str
    session_id: str
    messages: str
    stream: bool = False
