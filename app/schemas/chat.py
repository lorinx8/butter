from pydantic import BaseModel

class ChatRequest(BaseModel):
    # 提示词ID
    prompt_id: str
    # 会话ID
    session_id: str
    # 消息内容
    message_content: str

class ChatResponse(BaseModel):
    message: str 