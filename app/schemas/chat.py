from pydantic import BaseModel

class ChatRequest(BaseModel):
    message_content: str

class ChatResponse(BaseModel):
    message: str 