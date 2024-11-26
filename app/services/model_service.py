from typing import List, Dict
from fastapi import HTTPException
from app.repositories.model_repository import ModelRepository
from app.repositories.model_provider_repository import ModelProviderRepository
from app.schemas.model import ModelCreate, ModelUpdate
from app.repositories.models import Model
from sqlalchemy.exc import IntegrityError


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
        try:
            # 验证属性
            self.validate_properties(
                model_data.provider, model_data.properties)

            return self.model_repository.create(
                name=model_data.name,
                provider=model_data.provider,
                deploy_name=model_data.deploy_name,
                properties=model_data.properties,
                is_active=model_data.is_active
            )
        except IntegrityError as e:
            if "uq_model_deploy_name" in str(e):
                raise HTTPException(
                    status_code=400,
                    detail=f"Model with deploy_name '{model_data.deploy_name}' already exists"
                )
            raise e

    def get_model(self, model_id: str) -> Model:
        model = self.model_repository.get_by_id(model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return model

    def get_models(self, skip: int = 0, limit: int = 100) -> List[Model]:
        return self.model_repository.get_all(skip=skip, limit=limit)

    def get_active_models(self) -> List[Model]:
        return self.model_repository.get_active_models()

    def get_by_deploy_name(self, deploy_name: str) -> Model:
        return self.model_repository.get_by_deploy_name(deploy_name)

    def get_model_name_by_deploy_name(self, deploy_name: str) -> str:
        """
        根据部署名称获取模型提供商真正的模型名称
        """
        model = self.get_by_deploy_name(deploy_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        provider = model.provider
        # 不同的provider从不同的属性字段中获取真正的模型名称
        if provider == "openai":
            return model.properties["model"]
        elif provider == "azure_openai":
            return model.properties["deployment_name"]
        return ""

    def get_provider_and_model_name_by_deploy_name(self, deploy_name: str) -> (str, str):
        """
        根据部署名称获取模型提供商和真正的模型名称
        """
        model = self.get_by_deploy_name(deploy_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        provider = model.provider
        model_name = ''
        # 不同的provider从不同的属性字段中获取真正的模型名称
        if provider == "openai":
            model = model.properties["model"]
        return provider, model

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
