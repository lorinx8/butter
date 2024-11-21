from sqlalchemy import Boolean, Column, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())

# 定义账户


class Account(Base):
    __tablename__ = "account"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 定义账户令牌


class AccountToken(Base):
    __tablename__ = "account_token"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    account_id = Column(String(36), ForeignKey("account.id"))
    token = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 定义管理员用户


class AdminUser(Base):
    __tablename__ = "admin_user"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    telephone = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 定义提示词


class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 定义模型


class Model(Base):
    __tablename__ = "model"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    is_openai_compatible = Column(Boolean, default=False)
    properties = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# 字典分组表
class DictGroup(Base):
    __tablename__ = "dict_group"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    parent_id = Column(String(36), ForeignKey(
        "dict_group.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# 字典值表
class Dict(Base):
    __tablename__ = "dict"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(String(255), nullable=False)
    value_type = Column(String(50), nullable=False)  # integer, decimal, string
    description = Column(Text)
    group_id = Column(String(36), ForeignKey(
        "dict_group.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
