from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories import models
from app.utils.code_generator import generate_code


class DictRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, value: str, value_type: str, group_id: str,
               key: Optional[str] = None, description: Optional[str] = None) -> models.Dict:
        # 生成key
        final_key = generate_code("dict", key)

        db_value = models.Dict(
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

    def get_by_id(self, value_id: str) -> Optional[models.Dict]:
        return self.db.query(models.Dict).filter(models.Dict.id == value_id).first()

    def get_by_key(self, key: str) -> Optional[models.Dict]:
        return self.db.query(models.Dict).filter(models.Dict.key == key).first()

    def get_by_group(self, group_id: str) -> List[models.Dict]:
        return self.db.query(models.Dict).filter(models.Dict.group_id == group_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Dict]:
        return self.db.query(models.Dict).offset(skip).limit(limit).all()

    def update(self, value_id: str, **kwargs) -> Optional[models.Dict]:
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
