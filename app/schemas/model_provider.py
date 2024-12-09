from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ModelProviderBase(BaseModel):
    code: str
    name: str
    metadatas: Optional[Dict] = None
    description: Optional[str] = None
    is_active: bool = True


class ModelProviderInDB(ModelProviderBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
