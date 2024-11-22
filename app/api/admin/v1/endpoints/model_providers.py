from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.core.response import success_response, error_response
from app.core.error_code import ErrorCode
from app.repositories.model_provider_repository import ModelProviderRepository
from app.services.model_provider_service import ModelProviderService
from app.schemas.model_provider import ModelProviderInDB

router = APIRouter()


def get_provider_service(db: Session = Depends(get_db)):
    return ModelProviderService(ModelProviderRepository(db))


@router.get("/model-providers")
async def get_providers(
    skip: int = 0,
    limit: int = 100,
    token: dict = Depends(verify_token),
    provider_service: ModelProviderService = Depends(get_provider_service)
):
    try:
        providers = provider_service.get_providers(skip=skip, limit=limit)
        return success_response(data=providers)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/model-providers/{provider_id}")
async def get_provider(
    provider_id: str,
    token: dict = Depends(verify_token),
    provider_service: ModelProviderService = Depends(get_provider_service)
):
    try:
        provider = provider_service.get_provider(provider_id)
        return success_response(data=provider)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/model-providers/search")
async def search_providers(
    code: Optional[str] = None,
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    token: dict = Depends(verify_token),
    provider_service: ModelProviderService = Depends(get_provider_service)
):
    try:
        filters = {}
        if code:
            filters['code'] = code
        if name:
            filters['name'] = name
        if is_active is not None:
            filters['is_active'] = is_active

        providers = provider_service.search_providers(filters)
        return success_response(data=providers)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
