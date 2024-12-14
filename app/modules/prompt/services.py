from typing import Optional, List

from fastapi import HTTPException

from app.core.utils import code_generator
from app.modules.prompt.models import Prompt
from app.modules.prompt.repositories import PromptRepository
from app.modules.prompt.schemas import PromptCreate, PromptUpdate


class PromptService:
    def __init__(self, prompt_repository: PromptRepository):
        self.prompt_repository = prompt_repository

    def create_prompt(self, prompt_data: PromptCreate) -> Prompt:
        if prompt_data.code:
            existing = self.prompt_repository.get_by_code(prompt_data.code)
            if existing:
                raise HTTPException(
                    status_code=400, detail="Prompt code already exists")

        if not prompt_data.code:
            prompt_data.code = code_generator.generate_code("prompt")

        return self.prompt_repository.create(
            code=prompt_data.code,
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

    def get_prompt_by_code(self, code: str) -> Optional[Prompt]:
        return self.prompt_repository.get_by_code(code)

    def get_prompt_content_by_code(self, code: str) -> Optional[str]:
        prompt = self.prompt_repository.get_by_code(code)
        if prompt:
            return prompt.content
        return None

    def search_prompts(self, query: str) -> List[Prompt]:
        return self.prompt_repository.search(query)

    def update_prompt(self, prompt_id: str, prompt_data: PromptUpdate) -> Prompt:
        existing = self.prompt_repository.get_by_id(prompt_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Prompt not found")

        if prompt_data.code:
            code_exists = self.prompt_repository.get_by_code(prompt_data.code)
            if code_exists and code_exists.id != prompt_id:
                raise HTTPException(
                    status_code=400, detail="Prompt code already exists")

        update_data = prompt_data.model_dump(exclude_unset=True)
        prompt = self.prompt_repository.update(prompt_id, **update_data)
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        if not self.prompt_repository.delete(prompt_id):
            raise HTTPException(status_code=404, detail="Prompt not found")
        return True
