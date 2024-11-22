from pydantic import BaseModel, field_validator
from typing import Optional, Dict
from datetime import datetime
import re


class ModelBase(BaseModel):
    name: str
    provider: str
    deploy_name: str
    properties: Optional[Dict] = None
    is_active: bool = True

    @field_validator('deploy_name')
    @classmethod
    def validate_deploy_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', v):
            raise ValueError(
                'deploy_name must start with a letter and can only contain letters, numbers and underscores ')
        return v


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    deploy_name: Optional[str] = None
    properties: Optional[Dict] = None
    is_active: Optional[bool] = None

    @field_validator('deploy_name')
    @classmethod
    def validate_deploy_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError(
                'deploy_name must start with a letter and can only contain letters, numbers and underscores')
        return v


class ModelInDB(ModelBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
