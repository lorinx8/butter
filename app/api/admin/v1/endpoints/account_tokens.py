from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.repositories.account_token_repository import AccountTokenRepository
from app.services.account_token_service import AccountTokenService
from app.schemas.account_token import AccountTokenCreate, AccountTokenUpdate, AccountTokenInDB

router = APIRouter()

def get_token_service(db: Session = Depends(get_db)):
    return AccountTokenService(AccountTokenRepository(db))

@router.post("/account-tokens/", response_model=AccountTokenInDB)
async def create_token(
    token_data: AccountTokenCreate,
    token_service: AccountTokenService = Depends(get_token_service)
):
    return token_service.create_token(token_data)

@router.get("/account-tokens/", response_model=List[AccountTokenInDB])
async def get_tokens(
    skip: int = 0,
    limit: int = 100,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    return token_service.get_tokens(skip=skip, limit=limit)

@router.get("/account-tokens/{token_id}", response_model=AccountTokenInDB)
async def get_token(
    token_id: str,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    return token_service.get_token(token_id)

@router.get("/accounts/{account_id}/tokens", response_model=List[AccountTokenInDB])
async def get_account_tokens(
    account_id: str,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    return token_service.get_account_tokens(account_id)

@router.put("/account-tokens/{token_id}", response_model=AccountTokenInDB)
async def update_token(
    token_id: str,
    token_data: AccountTokenUpdate,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    return token_service.update_token(token_id, token_data)

@router.delete("/account-tokens/{token_id}")
async def delete_token(
    token_id: str,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    token_service.delete_token(token_id)
    return {"message": "Token deleted successfully"} 