from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.security import verify_token
from app.core.database.db_base import get_db
from app.core.exceptions.error_code import ErrorCode
from app.core.schemas.response import success_response, error_response

from app.modules.auth.repositories import AdminUserRepository
from app.modules.auth.services import UserService, create_user_token
from app.modules.auth.schemas import UserCreate, UserUpdate, UserLogin

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)):
    return UserService(AdminUserRepository(db))


@router.post("/admin-users", status_code=201)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = user_service.create_user(user_data)
        return success_response(data=user, message="User created successfully")
    except ValueError as e:
        return error_response(ErrorCode.USER_ALREADY_EXISTS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/admin-users")
async def get_users(
    _: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        users = user_service.get_users()
        return success_response(data=users)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/admin-users/{user_id}")
async def get_user(
    user_id: str,
    _: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = user_service.get_user(user_id)
        if not user:
            return error_response(ErrorCode.USER_NOT_FOUND, f"User {user_id} not found")
        return success_response(data=user)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/admin-users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    _: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = user_service.update_user(user_id, user_data)
        if not user:
            return error_response(ErrorCode.USER_NOT_FOUND, f"User {user_id} not found")
        return success_response(data=user, message="User updated successfully")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/admin-users/{user_id}")
async def delete_user(
    user_id: str,
    _: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user_service.delete_user(user_id)
        return success_response(message="User deleted successfully")
    except ValueError as e:
        return error_response(ErrorCode.USER_NOT_FOUND, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.post("/login")
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = user_service.authenticate_user(
            login_data.email, login_data.password)
        if not user:
            return error_response(
                ErrorCode.LOGIN_FAILED,
                "Incorrect email or password"
            )
        token = create_user_token(user)
        return success_response(data=token)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
