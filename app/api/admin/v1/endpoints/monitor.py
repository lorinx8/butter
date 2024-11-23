"""
Monitor endpoints for admin API.
This module provides monitoring endpoints for various system components.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_token
from app.core.response import success_response
from app.managers.llm.model_pool import ModelPool

router = APIRouter()


@router.get("/model-pool")
async def get_model_pool_status(
        token: dict = Depends(verify_token),
):
    """
    获取模型部署池的状态信息

    Returns:
        List[Dict]: 包含所有模型池的状态信息列表，每个模型包含：
        - deploy_name: 部署名称
        - name: 模型名称
        - provider: 提供商
        - pool_size: 池大小
        - active_instances: 当前活跃的实例数
    """
    pool = await ModelPool.get_instance()
    status = pool.get_pool_status()
    return success_response(data=status)
