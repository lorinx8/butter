from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Dict
from app.repositories import models


class ModelProviderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, provider_id: str) -> Optional[models.ModelProvider]:
        return self.db.query(models.ModelProvider).filter(models.ModelProvider.id == provider_id).first()

    def get_by_code(self, code: str) -> Optional[models.ModelProvider]:
        return self.db.query(models.ModelProvider).filter(models.ModelProvider.code == code).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.ModelProvider]:
        return self.db.query(models.ModelProvider).offset(skip).limit(limit).all()

    def search(self, filters: Dict) -> List[models.ModelProvider]:
        query = self.db.query(models.ModelProvider)
        conditions = []

        if filters.get('code'):
            conditions.append(models.ModelProvider.code == filters['code'])

        if filters.get('name'):
            conditions.append(
                models.ModelProvider.name.ilike(f"%{filters['name']}%"))

        if 'is_active' in filters:
            conditions.append(models.ModelProvider.is_active ==
                              filters['is_active'])

        if conditions:
            query = query.filter(and_(*conditions))

        return query.all()
