from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories import models
from app.utils.code_generator import generate_code


class DictGroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, code: Optional[str] = None, description: Optional[str] = None,
               is_system: bool = False, parent_id: Optional[str] = None) -> models.DictGroup:
        # 生成编码
        final_code = generate_code("group", code)

        db_group = models.DictGroup(
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

    def get_by_id(self, group_id: str) -> Optional[models.DictGroup]:
        return self.db.query(models.DictGroup).filter(models.DictGroup.id == group_id).first()

    def get_by_code(self, code: str) -> Optional[models.DictGroup]:
        return self.db.query(models.DictGroup).filter(models.DictGroup.code == code).first()

    def get_children(self, parent_id: Optional[str]) -> List[models.DictGroup]:
        return self.db.query(models.DictGroup).filter(models.DictGroup.parent_id == parent_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.DictGroup]:
        return self.db.query(models.DictGroup).offset(skip).limit(limit).all()

    def update(self, group_id: str, **kwargs) -> Optional[models.DictGroup]:
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
