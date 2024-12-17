from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB

# 定义机器人
from app.core.database.models.base import BaseModel


class Bot(BaseModel):
    __tablename__ = "bot"

    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    bot_type = Column(String(50), nullable=False)  # standard, customized
    properties = Column(JSONB)
    description = Column(Text)
    version = Column(String(50), nullable=False)