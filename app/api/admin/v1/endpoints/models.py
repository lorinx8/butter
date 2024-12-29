from fastapi import APIRouter, Depends
from app.core.logging import logger
from sqlalchemy.orm import Session

from app.core.auth.security import verify_token
from app.core.database.db_base import get_db
from app.core.exceptions.error_code import ErrorCode
from app.core.schemas.response import success_response, error_response
from app.modules.llm.repositories import ModelRepository, ModelProviderRepository
from app.modules.llm.schemas import ModelsCreate, ModelsUpdate
from app.modules.llm.services import ModelService

router = APIRouter()


def get_model_service(db: Session = Depends(get_db)):
    return ModelService(
        ModelRepository(db),
        ModelProviderRepository(db)
    )


@router.post("/models")
async def create_model(
    model_data: ModelsCreate,
    model_service: ModelService = Depends(get_model_service)
):
    try:
        model = model_service.create_model(model_data)
        return success_response(data=model, message="Model created successfully")
    except ValueError as e:
        logger.error(e)
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        logger.error(e)
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/models")
async def get_models(
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    try:
        models = model_service.get_models(skip=skip, limit=limit)
        return success_response(data=models)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/models/{model_id}")
async def get_model(
    model_id: str,
    _: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    try:
        model = model_service.get_model(model_id)
        if not model:
            return error_response(ErrorCode.NOT_FOUND, f"Model {model_id} not found")
        return success_response(data=model)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/models/{model_id}")
async def update_model(
    model_id: str,
    model_data: ModelsUpdate,
    _: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    try:
        model = model_service.update_model(model_id, model_data)
        if not model:
            return error_response(ErrorCode.NOT_FOUND, f"Model {model_id} not found")
        return success_response(data=model, message="Model updated successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    _: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    try:
        model_service.delete_model(model_id)
        return success_response(message="Model deleted successfully")
    except ValueError as e:
        return error_response(ErrorCode.NOT_FOUND, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
