#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: model_pool.py
@brief: 模型池管理API端点
@details:
    - 提供模型池状态查询
    - 提供模型池刷新功能
    - 提供刷新单个模型的功能
@date: 2024-11-23
@author: bukp
@version: 1.0
"""

from fastapi import APIRouter, Depends

from app.core.auth.security import verify_token
from app.core.schemas.response import success_response
from app.modules.llm.business.model_pool import ModelPool

router = APIRouter()


@router.get("/model-pool/status")
async def get_pool_status(
    _: dict = Depends(verify_token)
):
    """
    获取模型池状态
    - 返回所有模型的状态信息，包括并发限制和可用槽位
    """
    pool = await ModelPool.get_instance()
    status = await pool.get_pool_status()
    return success_response(data=status)


@router.post("/model-pool/refresh")
async def refresh_pool(
    _: dict = Depends(verify_token)
):
    """
    刷新模型池
    - 同步数据库中的模型到模型池
    - 添加新模型，移除已删除模型
    """
    pool = await ModelPool.get_instance()
    result = await pool.refresh_pool()
    return success_response(data=result)


@router.post("/model-pool/refresh/{deploy_name}")
async def refresh_model(
    deploy_name: str,
    _: dict = Depends(verify_token)
):
    """
    刷新指定模型
    - 根据deploy_name刷新指定模型的实例
    - 使用数据库中的最新配置更新模型
    Args:
        deploy_name: 模型的部署名称
    """
    pool = await ModelPool.get_instance()
    await pool.refresh_model(deploy_name)
    return success_response(message=f"Successfully refreshed model {deploy_name}")
