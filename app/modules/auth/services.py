from datetime import timedelta
from typing import List, Optional

from fastapi import HTTPException

from app.core.auth.security import create_access_token, verify_password
from app.core.config import settings
from app.modules.auth.models import Account, AccountToken
from app.modules.auth.repositories import AccountRepository, AccountTokenRepository, AdminUserRepository
from app.modules.auth.schemas import AccountCreate, AccountUpdate, AccountTokenCreate, AccountTokenUpdate, UserCreate, \
    UserInDB, UserUpdate


# ------------------------------------------ AccountService ------------------------------------------

class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def create_account(self, account_data: AccountCreate) -> Account:
        if self.account_repository.get_by_email(account_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        return self.account_repository.create(
            email=account_data.email,
            username=account_data.username,
            password=account_data.password
        )

    def get_account(self, account_id: str) -> Account:
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    def get_accounts(self, skip: int = 0, limit: int = 100) -> List[Account]:
        return self.account_repository.get_all(skip=skip, limit=limit)

    def update_account(self, account_id: str, account_data: AccountUpdate) -> Account:
        update_data = account_data.model_dump(exclude_unset=True)
        account = self.account_repository.update(account_id, **update_data)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

    def delete_account(self, account_id: str) -> bool:
        if not self.account_repository.delete(account_id):
            raise HTTPException(status_code=404, detail="Account not found")
        return True


# ------------------------------------------ AccountService ------------------------------------------

class AccountTokenService:
    def __init__(self, token_repository: AccountTokenRepository):
        self.token_repository = token_repository

    def create_token(self, token_data: AccountTokenCreate) -> AccountToken:
        return self.token_repository.create(
            account_id=token_data.account_id,
            token=token_data.token,
            description=token_data.description
        )

    def get_token(self, token_id: str) -> AccountToken:
        token = self.token_repository.get_by_id(token_id)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        return token

    def get_tokens(self, skip: int = 0, limit: int = 100) -> List[AccountToken]:
        return self.token_repository.get_all(skip=skip, limit=limit)

    def get_account_tokens(self, account_id: str) -> List[AccountToken]:
        return self.token_repository.get_by_account_id(account_id)

    def update_token(self, token_id: str, token_data: AccountTokenUpdate) -> AccountToken:
        update_data = token_data.model_dump(exclude_unset=True)
        token = self.token_repository.update(token_id, **update_data)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        return token

    def delete_token(self, token_id: str) -> bool:
        if not self.token_repository.delete(token_id):
            raise HTTPException(status_code=404, detail="Token not found")
        return True


# ------------------------------------------ User Service ------------------------------------------

def create_user_token(user: UserInDB) -> dict:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


class UserService:
    def __init__(self, user_repository: AdminUserRepository):
        self.user_repository = user_repository

    def create_user(self, user_data: UserCreate) -> UserInDB:
        if self.user_repository.get_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        user = self.user_repository.create(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password
        )
        return UserInDB.model_validate(user)

    def get_user(self, user_id: str) -> Optional[UserInDB]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserInDB.model_validate(user)

    def get_users(self) -> List[UserInDB]:
        users = self.user_repository.get_all()
        return [UserInDB.model_validate(user) for user in users]

    def update_user(self, user_id: str, user_data: UserUpdate) -> UserInDB:
        update_data = user_data.model_dump(exclude_unset=True)
        user = self.user_repository.update(user_id, **update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserInDB.model_validate(user)

    def delete_user(self, user_id: str) -> bool:
        if not self.user_repository.delete(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        return True

    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return UserInDB.model_validate(user)

