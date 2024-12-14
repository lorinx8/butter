import uuid
from typing import Dict, Any
from sqlalchemy import Column, DateTime, UUID
from sqlalchemy.sql import func

from app.core.database.db_base import Base

class BaseModel(Base):
    """所有模型的基类"""
    __abstract__ = True

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True),
                        onupdate=func.now(), nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """从字典创建模型实例"""
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__table__.columns
        })
