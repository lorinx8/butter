from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin, Token

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)):
    return UserService(UserRepository(db))

@router.post("/users/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.create_user(user_data)

@router.get("/users/", response_model=List[UserResponse])
async def get_users(
    token: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_users()

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    token: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_user(user_id)

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    token: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    return user_service.update_user(user_id, user_data)

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    token: dict = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
):
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}

@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    user = user_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_service.create_user_token(user) 