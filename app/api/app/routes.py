from fastapi import APIRouter
from app.schemas import chat

router = APIRouter()

router.include_router(chat.router, tags=["Chat"])