#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: bot_pool.py
@brief: 机器人池管理API端点
@details:
    - 提供机器人池状态查询
    - 提供机器人池刷新功能
    - 提供刷新单个机器人的功能
@date: 2024-01-17
@author: bukp
@version: 1.0
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_token
from app.managers.bot.bot_manager import BotManager
from app.core.response import success_response

router = APIRouter()


@router.get("/bot-pool/status")
async def get_pool_status(
    _: dict = Depends(verify_token)
):
    """
    获取机器人池状态
    - 返回所有机器人的状态信息，包括并发限制和可用槽位
    """
    manager = await BotManager.get_instance()
    status = await manager.bot_pool.get_pool_status()
    return success_response(data=status)


@router.post("/bot-pool/refresh")
async def refresh_pool(
    _: dict = Depends(verify_token)
):
    """
    刷新机器人池
    - 同步数据库中的机器人到机器人池
    - 添加新机器人，移除已删除机器人
    - 如果配置有改变，重新加载配置
    """
    manager = await BotManager.get_instance()
    result = await manager.refresh_pool()
    return success_response(data=result)


@router.post("/bot-pool/refresh/{bot_id}")
async def refresh_bot(
    bot_id: str,
    _: dict = Depends(verify_token)
):
    """
    刷新指定机器人
    - 根据bot_id刷新指定机器人的实例
    - 使用数据库中的最新配置更新机器人
    Args:
        bot_id: 机器人的ID
    """
    manager = await BotManager.get_instance()
    # 先移除旧的机器人实例
    await manager.remove_bot(bot_id)
    # 重新加载机器人到池中
    await manager.load_bots_to_pool()
    return success_response(message=f"Successfully refreshed bot {bot_id}")
