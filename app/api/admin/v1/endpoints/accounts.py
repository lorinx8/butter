from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.repositories.account_repository import AccountRepository
from app.services.account_service import AccountService
from app.schemas.account import AccountCreate, AccountUpdate, AccountInDB

router = APIRouter()

def get_account_service(db: Session = Depends(get_db)):
    return AccountService(AccountRepository(db))

@router.post("/accounts/", response_model=AccountInDB)
async def create_account(
    account_data: AccountCreate,
    account_service: AccountService = Depends(get_account_service)
):
    return account_service.create_account(account_data)

@router.get("/accounts/", response_model=List[AccountInDB])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    token: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    return account_service.get_accounts(skip=skip, limit=limit)

@router.get("/accounts/{account_id}", response_model=AccountInDB)
async def get_account(
    account_id: str,
    token: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    return account_service.get_account(account_id)

@router.put("/accounts/{account_id}", response_model=AccountInDB)
async def update_account(
    account_id: str,
    account_data: AccountUpdate,
    token: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    return account_service.update_account(account_id, account_data)

@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: str,
    token: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    account_service.delete_account(account_id)
    return {"message": "Account deleted successfully"} 