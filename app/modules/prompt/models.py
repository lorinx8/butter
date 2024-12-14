from sqlalchemy import Column, String, Text, Boolean

from app.core.database.models.base import BaseModel

# 定义提示词
class Prompt(BaseModel):
    __tablename__ = "prompt"

    code = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
