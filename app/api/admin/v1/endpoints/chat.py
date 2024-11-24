#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: chat.py
@brief: 管理员聊天API端点
@details:
    - 提供管理员级别的模型调用接口
    - 支持流式和非流式输出
    - 直接调用底层模型，不经过提示词处理
@date: 2024-11-23
@author: bukp
@version: 1.0
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.model_chat import ModelChatRequest
from app.core.security import verify_token
from app.core.response import success_response
from app.managers.chat.basic_chat import BasicChat

router = APIRouter()


@router.post("/chat/completions")
async def admin_chat(
    request: ModelChatRequest,
    token: dict = Depends(verify_token),  # Ensure admin access
):
    """
    管理员聊天接口
    - 直接调用底层模型，不经过提示词处理
    - 支持流式和非流式输出
    """
    if request.stream:
        async def generate():
            async for chunk in BasicChat.chat(
                deploy_name=request.model,
                messages=request.messages,
                stream=True
            ):
                yield f"data: {chunk}\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await BasicChat.chat(
            deploy_name=request.model,
            messages=request.messages,
            stream=False
        )
        return success_response(data={"message": response})
