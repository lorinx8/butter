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

from fastapi import APIRouter, Depends, Body
from fastapi.responses import StreamingResponse
from app.schemas.chat import ModelChatRequest, BotChatRequest
from app.core.security import verify_token
from app.core.response import success_response
from app.managers.chat.basic_chat import BasicChat
from app.managers.chat.bot_chat import BotChat

router = APIRouter()


@router.post("/chat/completions")
async def admin_chat(
    request: ModelChatRequest,
    _: dict = Depends(verify_token),  # Ensure admin access
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


@router.post("/bot/chat/completions")
async def bot_chat_stream(
    request: BotChatRequest,
    _: dict = Depends(verify_token),
):
    """
    机器人流式聊天接口
    """
    if request.stream:
        bot_id = request.bot_id
        messages = request.messages
        return StreamingResponse(
            BotChat.chat(bot_id, messages, stream=True),
            media_type="text/event-stream")
    else:
        bot_id = request.bot_id
        session_id = request.session_id
        messages = request.messages
        response = await BotChat.chat(bot_id, session_id, messages)
        return success_response(data={"message": response})