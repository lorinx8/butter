from typing import List, Optional
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserInDB

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreate) -> UserInDB:
        if self.user_repository.get_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = self.user_repository.create(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        return UserInDB.from_orm(user)

    def get_user(self, user_id: int) -> Optional[UserInDB]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserInDB.from_orm(user)

    def get_users(self) -> List[UserInDB]:
        users = self.user_repository.get_all()
        return [UserInDB.from_orm(user) for user in users]

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserInDB:
        update_data = user_data.dict(exclude_unset=True)
        user = self.user_repository.update(user_id, **update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserInDB.from_orm(user)

    def delete_user(self, user_id: int) -> bool:
        if not self.user_repository.delete(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return True 