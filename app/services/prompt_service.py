from typing import List, Optional
from fastapi import HTTPException
from app.repositories.prompt_repository import PromptRepository
from app.schemas.chat_prompt import ChatPromptCreate, ChatPromptUpdate
from app.services.prompt_cache_service import PromptCacheService
from app.repositories.models import Prompt

class PromptService:
    def __init__(self, prompt_repository: PromptRepository):
        self.prompt_repository = prompt_repository
        self.cache_service = PromptCacheService()

        self.refresh_cache()

    def create_prompt(self, prompt_data: ChatPromptCreate) -> Prompt:
        prompt = self.prompt_repository.create(
            name=prompt_data.name,
            content=prompt_data.content,
            description=prompt_data.description
        )
        self.cache_service.set(prompt)
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        # First try cache
        prompt = self.cache_service.get(prompt_id)
        if prompt:
            return prompt
        
        # If not in cache, get from DB
        prompt = self.prompt_repository.get_by_id(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Add to cache
        self.cache_service.set(prompt)
        return prompt

    def get_prompts(self, skip: int = 0, limit: int = 100) -> List[Prompt]:
        return self.prompt_repository.get_all(skip=skip, limit=limit)

    def update_prompt(self, prompt_id: str, prompt_data: ChatPromptUpdate) -> Prompt:
        update_data = prompt_data.model_dump(exclude_unset=True)
        prompt = self.prompt_repository.update(prompt_id, **update_data)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        self.cache_service.set(prompt)
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        if not self.prompt_repository.delete(prompt_id):
            raise HTTPException(status_code=404, detail="Prompt not found")
        self.cache_service.delete(prompt_id)
        return True

    def refresh_cache(self, prompt_id: Optional[str] = None) -> None:
        if prompt_id:
            prompt = self.prompt_repository.get_by_id(prompt_id)
            if prompt:
                self.cache_service.set(prompt)
        else:
            self.cache_service.clear()
            prompts = self.prompt_repository.get_all()
            for prompt in prompts:
                self.cache_service.set(prompt)

    def get_cached_prompts(self) -> List[Prompt]:
        return self.cache_service.get_all()