from fastapi import APIRouter, Depends
from app.core.security import verify_token
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
# 创建一个全局的 ChatService 实例
chat_service = ChatService()

def get_chat_service():
    return chat_service

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    token: dict = Depends(verify_token),
    chat_service: ChatService = Depends(get_chat_service)
):
    response = chat_service.chat(
        message_content=chat_request.message_content
    )
    return {"message": response} 