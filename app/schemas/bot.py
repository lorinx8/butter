from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Literal, Any


class BotBase(BaseModel):
    code: str
    name: str
    bot_type: str
    properties: Optional[Dict] = None
    description: Optional[str] = None


class BotStandardProperties(BaseModel):
    models_deploy_name: str
    models_prompt_code: str
    memory_enable: bool
    memory_strategy: Optional[Literal["tokens", "messages"]] = None
    max_tokens: Optional[int] = None
    max_message_rounds: Optional[int] = None


class BotStandardCreate(BotBase):
    properties: BotStandardProperties


class BotUpdate(BaseModel):
    name: Optional[str] = None
    bot_type: Optional[str] = None
    properties: Optional[Dict] = None
    description: Optional[str] = None


class BotInDB(BotBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
