from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.utils.code_generator import generate_code
from app.modules.dict.models import DictGroup, Dict


class DictGroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, code: Optional[str] = None, description: Optional[str] = None,
               is_system: bool = False, parent_id: Optional[str] = None) -> DictGroup:
        # 生成编码
        final_code = generate_code("group", code)

        db_group = DictGroup(
            code=final_code,
            name=name,
            description=description,
            is_system=is_system,
            parent_id=parent_id
        )
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def get_by_id(self, group_id: str) -> Optional[DictGroup]:
        return self.db.query(DictGroup).filter(DictGroup.id == group_id).first()

    def get_by_code(self, code: str) -> Optional[DictGroup]:
        return self.db.query(DictGroup).filter(DictGroup.code == code).first()

    def get_children(self, parent_id: Optional[str]) -> List[DictGroup]:
        return self.db.query(DictGroup).filter(DictGroup.parent_id == parent_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[DictGroup]:
        return self.db.query(DictGroup).offset(skip).limit(limit).all()

    def update(self, group_id: str, **kwargs) -> Optional[DictGroup]:
        group = self.get_by_id(group_id)
        if group:
            if 'code' in kwargs:
                kwargs['code'] = generate_code("group", kwargs['code'])
            for key, value in kwargs.items():
                setattr(group, key, value)
            self.db.commit()
            self.db.refresh(group)
        return group

    def delete(self, group_id: str) -> bool:
        group = self.get_by_id(group_id)
        if group:
            self.db.delete(group)
            self.db.commit()
            return True
        return False


class DictRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, value: str, value_type: str, group_id: str,
               key: Optional[str] = None, description: Optional[str] = None) -> Dict:
        # 生成key
        final_key = generate_code("dict", key)

        db_value = Dict(
            key=final_key,
            value=value,
            value_type=value_type,
            description=description,
            group_id=group_id
        )
        self.db.add(db_value)
        self.db.commit()
        self.db.refresh(db_value)
        return db_value

    def get_by_id(self, value_id: str) -> Optional[Dict]:
        return self.db.query(Dict).filter(Dict.id == value_id).first()

    def get_by_key(self, key: str) -> Optional[Dict]:
        return self.db.query(Dict).filter(Dict.key == key).first()

    def get_by_group(self, group_id: str) -> List[Dict]:
        return self.db.query(Dict).filter(Dict.group_id == group_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        return self.db.query(Dict).offset(skip).limit(limit).all()

    def update(self, value_id: str, **kwargs) -> Optional[Dict]:
        value = self.get_by_id(value_id)
        if value:
            if 'key' in kwargs:
                kwargs['key'] = generate_code("dict", kwargs['key'])
            for key, value_attr in kwargs.items():
                setattr(value, key, value_attr)
            self.db.commit()
            self.db.refresh(value)
        return value

    def delete(self, value_id: str) -> bool:
        value = self.get_by_id(value_id)
        if value:
            self.db.delete(value)
            self.db.commit()
            return True
        return False

