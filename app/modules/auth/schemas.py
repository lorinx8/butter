from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

# -------------------------------------------- Account --------------------------------------------

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

# -------------------------------------------- Account Token --------------------------------------------

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


# -------------------------------------------- Admin User --------------------------------------------


class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: UUID
    is_active: bool = True

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    pass

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"