from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatPromptBase(BaseModel):
    name: str
    content: str
    description: Optional[str] = None

class ChatPromptCreate(ChatPromptBase):
    pass

class ChatPromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ChatPromptInDB(ChatPromptBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True