from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.security import verify_token
from app.core.database.db_base import get_db
from app.core.schemas.error_code import ErrorCode
from app.core.schemas.response import success_response, error_response
from app.modules.llm.repositories import ModelProviderRepository
from app.modules.llm.services import ModelProviderService

router = APIRouter()


def get_provider_service(db: Session = Depends(get_db)):
    return ModelProviderService(ModelProviderRepository(db))


@router.get("/model-providers")
async def get_providers(
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(verify_token),
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
    _: dict = Depends(verify_token),
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
    _: dict = Depends(verify_token),
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
