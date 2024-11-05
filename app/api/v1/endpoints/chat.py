from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.database import get_db

router = APIRouter()

def get_chat_service(db: Session = Depends(get_db)):
    return ChatService(db)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    response = chat_service.chat(
        prompt_id=chat_request.prompt_id,
        session_id=chat_request.session_id, 
        message_content=chat_request.message_content
    )
    return {"message": response} 

@router.post("/chat/stream", response_model=ChatResponse)
async def chat_stream(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    async def generate():
        async for chunk in chat_service.chat_stream(
            prompt_id=chat_request.prompt_id,
            session_id=chat_request.session_id,
            message_content=chat_request.message_content
        ):
            # 确保每个chunk都是JSON格式，并以换行符结尾
            yield f"data: {chunk}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")