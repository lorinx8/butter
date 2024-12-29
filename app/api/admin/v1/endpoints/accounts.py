from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.security import verify_token
from app.core.database.db_base import get_db
from app.core.exceptions.error_code import ErrorCode
from app.core.schemas.response import success_response, error_response

from app.modules.auth.repositories import AccountRepository
from app.modules.auth.schemas import AccountCreate, AccountUpdate
from app.modules.auth.services import AccountService

router = APIRouter()


def get_account_service(db: Session = Depends(get_db)):
    return AccountService(AccountRepository(db))


@router.post("/accounts")
async def create_account(
    account_data: AccountCreate,
    account_service: AccountService = Depends(get_account_service)
):
    try:
        account = account_service.create_account(account_data)
        return success_response(data=account, message="Account created successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/accounts")
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        accounts = account_service.get_accounts(skip=skip, limit=limit)
        return success_response(data=accounts)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/accounts/{account_id}")
async def get_account(
    account_id: str,
    _: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        account = account_service.get_account(account_id)
        if not account:
            return error_response(ErrorCode.NOT_FOUND, f"Account {account_id} not found")
        return success_response(data=account)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/accounts/{account_id}")
async def update_account(
    account_id: str,
    account_data: AccountUpdate,
    _: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        account = account_service.update_account(account_id, account_data)
        if not account:
            return error_response(ErrorCode.NOT_FOUND, f"Account {account_id} not found")
        return success_response(data=account, message="Account updated successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: str,
    _: dict = Depends(verify_token),
    account_service: AccountService = Depends(get_account_service)
):
    try:
        account_service.delete_account(account_id)
        return success_response(message="Account deleted successfully")
    except ValueError as e:
        return error_response(ErrorCode.NOT_FOUND, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
