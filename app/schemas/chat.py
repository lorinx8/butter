from typing import List
from pydantic import BaseModel

# 消息
class Message(BaseModel):
    role: str
    content: str

# 聊天请求
class ChatRequest(BaseModel):
    # 模型
    model: str
    # 消息
    messages: List[Message]
    # 是否流式输出
    stream: bool = False

# 聊天响应
class ChatResponse(BaseModel):
    message: str 