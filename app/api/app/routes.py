from fastapi import APIRouter

from app.api.app.v1.endpoints import chat

router = APIRouter()

router.include_router(chat.router, tags=["💬 Chat"])
