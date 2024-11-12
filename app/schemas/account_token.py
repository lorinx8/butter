from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AccountTokenBase(BaseModel):
    account_id: str
    token: str
    description: Optional[str] = None

class AccountTokenCreate(AccountTokenBase):
    pass

class AccountTokenUpdate(BaseModel):
    token: Optional[str] = None
    description: Optional[str] = None

class AccountTokenInDB(AccountTokenBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 