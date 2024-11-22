from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories import models


class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, provider: str, deploy_name: str,
               properties: dict = None, is_active: bool = True) -> models.Model:
        db_model = models.Model(
            name=name,
            provider=provider,
            deploy_name=deploy_name,
            properties=properties,
            is_active=is_active
        )
        self.db.add(db_model)
        self.db.commit()
        self.db.refresh(db_model)
        return db_model

    def get_by_id(self, model_id: str) -> Optional[models.Model]:
        return self.db.query(models.Model).filter(models.Model.id == model_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Model]:
        return self.db.query(models.Model).offset(skip).limit(limit).all()

    def update(self, model_id: str, **kwargs) -> Optional[models.Model]:
        model = self.get_by_id(model_id)
        if model:
            for key, value in kwargs.items():
                setattr(model, key, value)
            self.db.commit()
            self.db.refresh(model)
        return model

    def delete(self, model_id: str) -> bool:
        model = self.get_by_id(model_id)
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False
