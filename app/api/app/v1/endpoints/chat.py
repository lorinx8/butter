#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: chat.py
@brief: 聊天API端点
@details:
    - 提供模型及智能体调用接口
    - 支持流式和非流式输出
@date: 2024-11-23
@author: bukp
@version: 1.0
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.auth.security import verify_token
from app.core.schemas.response import success_response
from app.modules.chat.business.basic_chat import BasicChat
from app.modules.chat.business.bot_chat import BotChat
from app.modules.chat.schemas import ModelChatRequest, BotChatRequest

router = APIRouter()


@router.post("/chat/completions")
async def chat(
    request: ModelChatRequest,
    _: dict = Depends(verify_token),  # Ensure admin access
):
    """
    聊天接口
    - 直接调用底层模型，不经过提示词处理
    - 支持流式和非流式输出
    """
    if request.stream:
        async def generate():
            chat_iterator = await BasicChat.chat(
                deploy_name=request.model,
                messages=request.messages,
                stream=True
            )
            async for chunk in chat_iterator:
                yield f"data: {chunk}\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await BasicChat.chat(
            deploy_name=request.model,
            messages=request.messages,
            stream=False
        )
        return success_response(data={"message": response})


@router.post("/bot/chat/completions")
async def bot_chat(
    request: BotChatRequest,
    _: dict = Depends(verify_token),
):
    """
    智能体聊天接口
    - 具备内置提示提、工具调用、历史记忆功能
    - 支持流式和非流式输出
    """
    if request.stream:
        async def generate():
            # 先获取异步迭代器
            chat_iterator = await BotChat.chat(
                request.bot_code,
                session_id=request.session_id,
                messages=request.messages,
                image_url=request.image_url,
                stream=True
            )
            # 对迭代器进行迭代
            async for chunk in chat_iterator:
                yield f"data: {chunk}\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await BotChat.chat(
            request.bot_code,
            request.session_id,
            request.messages,
            image_url=request.image_url,
            stream=False
        )
        return success_response(data={"message": response})
