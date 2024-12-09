from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PromptBase(BaseModel):
    name: str
    code: str
    content: str
    description: Optional[str] = None


class PromptCreate(PromptBase):
    code: Optional[str] = None
    pass


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PromptInDB(PromptBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
