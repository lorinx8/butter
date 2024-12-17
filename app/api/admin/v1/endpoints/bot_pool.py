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
from sqlalchemy.orm import Session

from app.core.auth.security import verify_token
from app.core.database.db_base import get_db
from app.core.schemas.response import success_response
from app.modules.bot.business.bot_manager import BotManager

router = APIRouter()


@router.get("/bot-pool/status")
async def get_pool_status(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)):
    """
    获取机器人池状态
    - 返回所有机器人的状态信息，包括并发限制和可用槽位
    """
    manager = await BotManager.get_instance(db)
    status = await manager.get_pool_status()
    return success_response(data=status)


@router.post("/bot-pool/refresh")
async def refresh_pool(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)):
    """
    刷新机器人池
    - 同步数据库中的机器人到机器人池
    - 添加新机器人，移除已删除机器人
    - 如果配置有改变，重新加载配置
    """
    manager = await BotManager.get_instance(db)
    result = await manager.refresh_pool()
    return success_response(data=result)


@router.post("/bot-pool/refresh/{bot_code}")
async def refresh_bot(
    bot_code: str,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """
    刷新指定机器人
    - 根据bot_id刷新指定机器人的实例
    - 使用数据库中的最新配置更新机器人
    Args:
        bot_code: 机器人的ID
        _: 验证token
    Returns:
        返回成功响应
    """
    manager = await BotManager.get_instance(db)
    # 先移除旧的机器人实例
    await manager.refresh_bot(bot_code)
    return success_response(message=f"Successfully refreshed bot {bot_code}")
