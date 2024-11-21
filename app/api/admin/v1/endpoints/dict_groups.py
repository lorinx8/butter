from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.response import success_response, error_response
from app.core.error_code import ErrorCode
from app.repositories.dict_group_repository import DictGroupRepository
from app.services.dict_group_service import DictGroupService
from app.schemas.dict import DictGroupCreate, DictGroupUpdate, DictGroupInDB

router = APIRouter()


def get_group_service(db: Session = Depends(get_db)):
    return DictGroupService(DictGroupRepository(db))


@router.post("/dict-groups")
async def create_group(
    group_data: DictGroupCreate,
    group_service: DictGroupService = Depends(get_group_service)
):
    try:
        group = group_service.create_group(group_data)
        return success_response(data=group, message="Dictionary group created successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/dict-groups")
async def get_groups(
    skip: int = 0,
    limit: int = 100,
    group_service: DictGroupService = Depends(get_group_service)
):
    try:
        groups = group_service.get_groups(skip=skip, limit=limit)
        return success_response(data=groups)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/dict-groups/{group_id}")
async def get_group(
    group_id: str,
    group_service: DictGroupService = Depends(get_group_service)
):
    try:
        group = group_service.get_group(group_id)
        return success_response(data=group)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/dict-groups/{parent_id}/children")
async def get_children(
    parent_id: str,
    group_service: DictGroupService = Depends(get_group_service)
):
    try:
        children = group_service.get_children(parent_id)
        return success_response(data=children)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/dict-groups/{group_id}")
async def update_group(
    group_id: str,
    group_data: DictGroupUpdate,
    group_service: DictGroupService = Depends(get_group_service)
):
    try:
        group = group_service.update_group(group_id, group_data)
        return success_response(data=group, message="Dictionary group updated successfully")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/dict-groups/{group_id}")
async def delete_group(
    group_id: str,
    group_service: DictGroupService = Depends(get_group_service)
):
    try:
        group_service.delete_group(group_id)
        return success_response(message="Dictionary group deleted successfully")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
