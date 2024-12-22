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

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.security import verify_token
from app.core.schemas.response import success_response
from app.core.database.db_base import get_async_db
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
    执行基础聊天
    """
    if request.stream:
        chat_iterator = BasicChat.chat_stream(
            request.model,
            request.messages,
        )
        return StreamingResponse(chat_iterator)
    else:
        response = await BasicChat.chat_sync(
            request.model,
            request.messages,
        )
        return success_response(data={"message": response})


@router.post("/bot/chat/completions")
async def bot_chat(
    request: BotChatRequest,
    db: AsyncSession = Depends(get_async_db),
    _: dict = Depends(verify_token),
):
    """
    执行机器人聊天
    """
    if request.stream:
        # 对迭代器进行迭代
        async def generate():
            chat_iterator = BotChat.chat_stream(
                bot_code=request.bot_code,
                session_id=request.session_id,
                messages=request.messages,
                db=db,
                image_url=request.image_url,
            )   
            async for chunk in chat_iterator:
                yield f"data: {chunk}\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await BotChat.chat(
            bot_code=request.bot_code,
            session_id=request.session_id,
            messages=request.messages,
            db=db,
            image_url=request.image_url,
        )
        return success_response(data={"message": response})
