from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ModelBase(BaseModel):
    name: str
    provider: str
    model: str
    is_openai_compatible: bool = False
    properties: Optional[Dict] = None
    is_active: bool = True

class ModelCreate(ModelBase):
    pass

class ModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    is_openai_compatible: Optional[bool] = None
    properties: Optional[Dict] = None
    is_active: Optional[bool] = None

class ModelInDB(ModelBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 