from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AccountBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True

class AccountCreate(AccountBase):
    password: str

class AccountUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class AccountInDB(AccountBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True 