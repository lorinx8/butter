from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.response import success_response, error_response
from app.core.error_code import ErrorCode
from app.repositories.dict_repository import DictRepository
from app.repositories.dict_group_repository import DictGroupRepository
from app.services.dict_service import DictService
from app.schemas.dict import DictCreate, DictUpdate

router = APIRouter()


def get_value_service(db: Session = Depends(get_db)):
    return DictService(
        DictRepository(db),
        DictGroupRepository(db)
    )


@router.post("/dicts")
async def create_value(
    value_data: DictCreate,
    value_service: DictService = Depends(get_value_service)
):
    try:
        value = value_service.create_value(value_data)
        return success_response(data=value, message="Dictionary value created successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/dicts")
async def get_values(
    skip: int = 0,
    limit: int = 100,
    value_service: DictService = Depends(get_value_service)
):
    try:
        values = value_service.get_values(skip=skip, limit=limit)
        return success_response(data=values)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/dicts/{value_id}")
async def get_value(
    value_id: str,
    value_service: DictService = Depends(get_value_service)
):
    try:
        value = value_service.get_value(value_id)
        return success_response(data=value)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/dicts/{group_id}/values")
async def get_values_by_group(
    group_id: str,
    value_service: DictService = Depends(get_value_service)
):
    try:
        values = value_service.get_values_by_group(group_id)
        return success_response(data=values)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/dicts/{value_id}")
async def update_value(
    value_id: str,
    value_data: DictUpdate,
    value_service: DictService = Depends(get_value_service)
):
    try:
        value = value_service.update_value(value_id, value_data)
        return success_response(data=value, message="Dictionary value updated successfully")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/dicts/{value_id}")
async def delete_value(
    value_id: str,
    value_service: DictService = Depends(get_value_service)
):
    try:
        value_service.delete_value(value_id)
        return success_response(message="Dictionary value deleted successfully")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
