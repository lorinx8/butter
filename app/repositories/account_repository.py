from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories import models
from app.core.security import get_password_hash

class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, username: str, password: str) -> models.Account:
        hashed_password = get_password_hash(password)
        db_account = models.Account(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account

    def get_by_id(self, account_id: str) -> Optional[models.Account]:
        return self.db.query(models.Account).filter(models.Account.id == account_id).first()

    def get_by_email(self, email: str) -> Optional[models.Account]:
        return self.db.query(models.Account).filter(models.Account.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[models.Account]:
        return self.db.query(models.Account).offset(skip).limit(limit).all()

    def update(self, account_id: str, **kwargs) -> Optional[models.Account]:
        account = self.get_by_id(account_id)
        if account:
            for key, value in kwargs.items():
                if key == 'password':
                    value = get_password_hash(value)
                    key = 'hashed_password'
                setattr(account, key, value)
            self.db.commit()
            self.db.refresh(account)
        return account

    def delete(self, account_id: str) -> bool:
        account = self.get_by_id(account_id)
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False 