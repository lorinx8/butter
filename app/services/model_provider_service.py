from typing import List, Optional, Dict
from fastapi import HTTPException
from app.repositories.model_provider_repository import ModelProviderRepository
from app.repositories.models import ModelProvider


class ModelProviderService:
    def __init__(self, provider_repository: ModelProviderRepository):
        self.provider_repository = provider_repository

    def get_provider(self, provider_id: str) -> Optional[ModelProvider]:
        provider = self.provider_repository.get_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        return provider

    def get_providers(self, skip: int = 0, limit: int = 100) -> List[ModelProvider]:
        return self.provider_repository.get_all(skip=skip, limit=limit)

    def search_providers(self, filters: Dict) -> List[ModelProvider]:
        return self.provider_repository.search(filters)
