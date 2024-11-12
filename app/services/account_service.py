from typing import List, Optional
from fastapi import HTTPException
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountUpdate
from app.repositories.models import Account

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