from sqlalchemy.orm import Session
from typing import List, Optional
from functools import lru_cache
from . import models
from sqlalchemy import or_

class PromptRepository:
    def __init__(self, db: Session):
        self.db = db

    @lru_cache(maxsize=1000)
    def get_by_id(self, prompt_id: str) -> Optional[models.Prompt]:
        return self.db.query(models.Prompt).filter(models.Prompt.id == prompt_id).first()

    def create(self, name: str, content: str, description: Optional[str] = None) -> models.Prompt:
        db_prompt = models.Prompt(
            name=name,
            content=content,
            description=description
        )
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)
        self.invalidate_cache(db_prompt.id)
        return db_prompt

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Prompt]:
        return self.db.query(models.Prompt).offset(skip).limit(limit).all()

    def update(self, prompt_id: str, **kwargs) -> Optional[models.Prompt]:
        prompt = self.get_by_id(prompt_id)
        if prompt:
            for key, value in kwargs.items():
                setattr(prompt, key, value)
            self.db.commit()
            self.db.refresh(prompt)
            self.invalidate_cache(prompt_id)
        return prompt

    def delete(self, prompt_id: str) -> bool:
        prompt = self.get_by_id(prompt_id)
        if prompt:
            self.db.delete(prompt)
            self.db.commit()
            self.invalidate_cache(prompt_id)
            return True
        return False

    def search(self, query: str) -> List[models.Prompt]:
        return self.db.query(models.Prompt).filter(
            or_(
                models.Prompt.name.ilike(f"%{query}%"),
                models.Prompt.description.ilike(f"%{query}%")
            )
        ).all()

    def invalidate_cache(self, prompt_id: str = None):
        if prompt_id:
            self.get_by_id.cache_clear()