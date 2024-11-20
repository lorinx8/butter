from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories import models
from app.core.security import get_password_hash

class AdminUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, username: str, password: str) -> models.AdminUser:
        hashed_password = get_password_hash(password)
        db_user = models.AdminUser(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: str) -> Optional[models.AdminUser]:
        return self.db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[models.AdminUser]:
        return self.db.query(models.AdminUser).filter(models.AdminUser.email == email).first()

    def get_all(self) -> List[models.AdminUser]:
        return self.db.query(models.AdminUser).all()

    def update(self, user_id: str, **kwargs) -> Optional[models.AdminUser]:
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if key == 'password':
                    value = get_password_hash(value)
                    key = 'hashed_password'
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False 