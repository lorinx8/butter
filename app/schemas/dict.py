from typing import Optional, List
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum

class ValueType(str, Enum):
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"


class DictGroupBase(BaseModel):
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    is_system: bool = False
    parent_id: Optional[str] = None


class DictGroupCreate(DictGroupBase):
    pass


class DictGroupUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_system: Optional[bool] = None
    parent_id: Optional[str] = None


class DictGroupInDB(DictGroupBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DictBase(BaseModel):
    key: Optional[str] = None
    value: str
    value_type: ValueType
    description: Optional[str] = None
    group_id: str


class DictCreate(DictBase):
    pass


class DictUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    value_type: Optional[ValueType] = None
    description: Optional[str] = None
    group_id: Optional[str] = None


class DictInDB(DictBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
