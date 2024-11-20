from typing import List
from fastapi import HTTPException
from app.repositories.account_token_repository import AccountTokenRepository
from app.schemas.account_token import AccountTokenCreate, AccountTokenUpdate
from app.repositories.models import AccountToken

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