from typing import List, Dict
from fastapi import HTTPException
from app.repositories.model_repository import ModelRepository
from app.repositories.model_provider_repository import ModelProviderRepository
from app.schemas.model import ModelCreate, ModelUpdate
from app.repositories.models import Model


class ModelService:
    def __init__(self, model_repository: ModelRepository, provider_repository: ModelProviderRepository):
        self.model_repository = model_repository
        self.provider_repository = provider_repository

    def validate_properties(self, provider_code: str, properties: Dict) -> None:
        provider = self.provider_repository.get_by_code(provider_code)
        if not provider:
            raise HTTPException(
                status_code=404, detail=f"Provider {provider_code} not found")

        # 获取元数据定义的字段
        required_fields = {item["field"] for item in provider.metadatas}

        # 验证提供的属性是否符合元数据定义
        if properties:
            provided_fields = set(properties.keys())
            invalid_fields = provided_fields - required_fields
            if invalid_fields:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid properties fields: {invalid_fields}"
                )

    def create_model(self, model_data: ModelCreate) -> Model:
        # 验证属性
        self.validate_properties(model_data.provider, model_data.properties)

        return self.model_repository.create(
            name=model_data.name,
            provider=model_data.provider,
            deploy_name=model_data.deploy_name,
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
