from typing import List, Optional
from fastapi import HTTPException
from app.repositories.prompt_repository import PromptRepository
from app.schemas.prompt import PromptCreate, PromptUpdate
from app.repositories.models import Prompt

class PromptService:
    def __init__(self, prompt_repository: PromptRepository):
        self.prompt_repository = prompt_repository

    def create_prompt(self, prompt_data: PromptCreate) -> Prompt:
        return self.prompt_repository.create(
            name=prompt_data.name,
            content=prompt_data.content,
            description=prompt_data.description
        )

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        prompt = self.prompt_repository.get_by_id(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt

    def get_prompts(self, skip: int = 0, limit: int = 100) -> List[Prompt]:
        return self.prompt_repository.get_all(skip=skip, limit=limit)

    def update_prompt(self, prompt_id: str, prompt_data: PromptUpdate) -> Prompt:
        update_data = prompt_data.model_dump(exclude_unset=True)
        prompt = self.prompt_repository.update(prompt_id, **update_data)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        if not self.prompt_repository.delete(prompt_id):
            raise HTTPException(status_code=404, detail="Prompt not found")
        return True