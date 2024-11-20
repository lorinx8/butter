from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.response import success_response, error_response
from app.core.error_code import ErrorCode
from app.repositories.account_token_repository import AccountTokenRepository
from app.services.account_token_service import AccountTokenService
from app.schemas.account_token import AccountTokenCreate, AccountTokenUpdate, AccountTokenInDB

router = APIRouter()

def get_token_service(db: Session = Depends(get_db)):
    return AccountTokenService(AccountTokenRepository(db))

@router.post("/account-tokens/")
async def create_token(
    token_data: AccountTokenCreate,
    token_service: AccountTokenService = Depends(get_token_service)
):
    try:
        token = token_service.create_token(token_data)
        return success_response(data=token, message="Token created successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))

@router.get("/account-tokens/")
async def get_tokens(
    skip: int = 0,
    limit: int = 100,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    try:
        tokens = token_service.get_tokens(skip=skip, limit=limit)
        return success_response(data=tokens)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))

@router.get("/account-tokens/{token_id}")
async def get_token(
    token_id: str,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    try:
        token = token_service.get_token(token_id)
        if not token:
            return error_response(ErrorCode.NOT_FOUND, f"Token {token_id} not found")
        return success_response(data=token)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))

@router.get("/accounts/{account_id}/tokens")
async def get_account_tokens(
    account_id: str,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    try:
        tokens = token_service.get_account_tokens(account_id)
        return success_response(data=tokens)
    except ValueError as e:
        return error_response(ErrorCode.NOT_FOUND, f"Account {account_id} not found")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))

@router.put("/account-tokens/{token_id}")
async def update_token(
    token_id: str,
    token_data: AccountTokenUpdate,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    try:
        token = token_service.update_token(token_id, token_data)
        if not token:
            return error_response(ErrorCode.NOT_FOUND, f"Token {token_id} not found")
        return success_response(data=token, message="Token updated successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))

@router.delete("/account-tokens/{token_id}")
async def delete_token(
    token_id: str,
    token: dict = Depends(verify_token),
    token_service: AccountTokenService = Depends(get_token_service)
):
    try:
        token_service.delete_token(token_id)
        return success_response(message="Token deleted successfully")
    except ValueError as e:
        return error_response(ErrorCode.NOT_FOUND, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))