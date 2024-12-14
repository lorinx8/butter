from typing import Optional, List, Dict

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.modules.llm.models import ModelProvider, Model


class ModelProviderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, provider_id: str) -> Optional[ModelProvider]:
        return self.db.query(ModelProvider).filter(ModelProvider.id == provider_id).first()

    def get_by_code(self, code: str) -> Optional[ModelProvider]:
        return self.db.query(ModelProvider).filter(ModelProvider.code == code).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelProvider]:
        return self.db.query(ModelProvider).offset(skip).limit(limit).all()

    def search(self, filters: Dict) -> List[ModelProvider]:
        query = self.db.query(ModelProvider)
        conditions = []

        if filters.get('code'):
            conditions.append(ModelProvider.code == filters['code'])

        if filters.get('name'):
            conditions.append(
                ModelProvider.name.ilike(f"%{filters['name']}%"))

        if 'is_active' in filters:
            conditions.append(ModelProvider.is_active ==
                              filters['is_active'])

        if conditions:
            query = query.filter(and_(*conditions))

        return query.all()


class ModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, provider: str, deploy_name: str,
               properties: dict = None, is_active: bool = True) -> Model:
        db_model = Model(
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

    def get_by_id(self, model_id: str) -> Optional[Model]:
        return self.db.query(Model).filter(Model.id == model_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Model]:
        return self.db.query(Model).offset(skip).limit(limit).all()

    def get_active_models(self) -> List[Model]:
        return self.db.query(Model).filter(Model.is_active == True).all()

    def get_by_deploy_name(self, deploy_name: str) -> Optional[Model]:
        return self.db.query(Model).filter(Model.deploy_name == deploy_name).first()

    def update(self, model_id: str, **kwargs) -> Optional[Model]:
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
