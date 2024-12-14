from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database.models.base import BaseModel


# 定义模型提供商
class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    metadatas = Column(JSONB)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

# 定义模型
class Model(BaseModel):
    __tablename__ = "model"

    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    deploy_name = Column(String(255), nullable=False, unique=True)
    properties = Column(JSONB)
    is_active = Column(Boolean, default=True)
