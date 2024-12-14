from sqlalchemy import Column, String, Text, Boolean

from app.core.database.models.base import BaseModel


# 字典分组表
class DictGroup(BaseModel):
    __tablename__ = "dict_group"

    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    parent_id = Column(String(36), nullable=True)


# 字典值表
class Dict(BaseModel):
    __tablename__ = "dict"

    key = Column(String(255), unique=True, nullable=False)
    value = Column(String(255), nullable=False)
    value_type = Column(String(50), nullable=False)  # integer, decimal, string
    description = Column(Text)
    group_id = Column(String(36), nullable=False)
