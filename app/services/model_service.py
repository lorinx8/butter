from typing import List
from fastapi import HTTPException
from app.repositories.model_repository import ModelRepository
from app.schemas.model import ModelCreate, ModelUpdate
from app.repositories.models import Model

class ModelService:
    def __init__(self, model_repository: ModelRepository):
        self.model_repository = model_repository

    def create_model(self, model_data: ModelCreate) -> Model:
        return self.model_repository.create(
            name=model_data.name,
            provider=model_data.provider,
            model=model_data.model,
            is_openai_compatible=model_data.is_openai_compatible,
            properties=model_data.properties,
            is_active=model_data.is_active
        )

    def get_model(self, model_id: str) -> Model:
        model = self.model_repository.get_by_id(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model

    def get_models(self, skip: int = 0, limit: int = 100) -> List[Model]:
        return self.model_repository.get_all(skip=skip, limit=limit)

    def update_model(self, model_id: str, model_data: ModelUpdate) -> Model:
        update_data = model_data.model_dump(exclude_unset=True)
        model = self.model_repository.update(model_id, **update_data)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model

    def delete_model(self, model_id: str) -> bool:
        if not self.model_repository.delete(model_id):
            raise HTTPException(status_code=404, detail="Model not found")
        return True 