from sqlalchemy import Column, String, Boolean

from app.core.database.models.base import BaseModel

# 定义账户
class Account(BaseModel):
    __tablename__ = "account"

    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


# 定义账户令牌
class AccountToken(BaseModel):
    __tablename__ = "account_token"

    account_id = Column(String(36))
    token = Column(String)
    description = Column(String)


# 定义管理员用户
class AdminUser(BaseModel):
    __tablename__ = "admin_user"

    email = Column(String, unique=True, index=True)
    telephone = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

