from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories import models

class AccountTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, account_id: str, token: str, description: Optional[str] = None) -> models.AccountToken:
        db_token = models.AccountToken(
            account_id=account_id,
            token=token,
            description=description
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_by_id(self, token_id: str) -> Optional[models.AccountToken]:
        return self.db.query(models.AccountToken).filter(models.AccountToken.id == token_id).first()

    def get_by_account_id(self, account_id: str) -> List[models.AccountToken]:
        return self.db.query(models.AccountToken).filter(models.AccountToken.account_id == account_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.AccountToken]:
        return self.db.query(models.AccountToken).offset(skip).limit(limit).all()

    def update(self, token_id: str, **kwargs) -> Optional[models.AccountToken]:
        token = self.get_by_id(token_id)
        if token:
            for key, value in kwargs.items():
                setattr(token, key, value)
            self.db.commit()
            self.db.refresh(token)
        return token

    def delete(self, token_id: str) -> bool:
        token = self.get_by_id(token_id)
        if token:
            self.db.delete(token)
            self.db.commit()
            return True
        return False 