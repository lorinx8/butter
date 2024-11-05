from sqlalchemy.orm import Session
from typing import List, Optional
from . import models
from sqlalchemy import or_

class ChatPromptRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, content: str, description: Optional[str] = None) -> models.ChatPrompt:
        db_prompt = models.ChatPrompt(
            name=name,
            content=content,
            description=description
        )
        self.db.add(db_prompt)
        self.db.commit()
        self.db.refresh(db_prompt)
        return db_prompt

    def get_by_id(self, prompt_id: str) -> Optional[models.ChatPrompt]:
        return self.db.query(models.ChatPrompt).filter(models.ChatPrompt.id == prompt_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.ChatPrompt]:
        return self.db.query(models.ChatPrompt).offset(skip).limit(limit).all()

    def update(self, prompt_id: str, **kwargs) -> Optional[models.ChatPrompt]:
        prompt = self.get_by_id(prompt_id)
        if prompt:
            for key, value in kwargs.items():
                setattr(prompt, key, value)
            self.db.commit()
            self.db.refresh(prompt)
        return prompt

    def delete(self, prompt_id: str) -> bool:
        prompt = self.get_by_id(prompt_id)
        if prompt:
            self.db.delete(prompt)
            self.db.commit()
            return True
        return False

    def search(self, query: str) -> List[models.ChatPrompt]:
        return self.db.query(models.ChatPrompt).filter(
            or_(
                models.ChatPrompt.name.ilike(f"%{query}%"),
                models.ChatPrompt.description.ilike(f"%{query}%")
            )
        ).all()