from fastapi import APIRouter

from app.api.app.v1.endpoints import chat, chat_history

router = APIRouter()

router.include_router(chat.router, tags=["💬 Chat"])
router.include_router(chat_history.router, tags=["💬 Chat History"])
