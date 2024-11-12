from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.repositories.model_repository import ModelRepository
from app.services.model_service import ModelService
from app.schemas.model import ModelCreate, ModelUpdate, ModelInDB

router = APIRouter()

def get_model_service(db: Session = Depends(get_db)):
    return ModelService(ModelRepository(db))

@router.post("/models/", response_model=ModelInDB)
async def create_model(
    model_data: ModelCreate,
    model_service: ModelService = Depends(get_model_service)
):
    return model_service.create_model(model_data)

@router.get("/models/", response_model=List[ModelInDB])
async def get_models(
    skip: int = 0,
    limit: int = 100,
    token: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    return model_service.get_models(skip=skip, limit=limit)

@router.get("/models/{model_id}", response_model=ModelInDB)
async def get_model(
    model_id: str,
    token: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    return model_service.get_model(model_id)

@router.put("/models/{model_id}", response_model=ModelInDB)
async def update_model(
    model_id: str,
    model_data: ModelUpdate,
    token: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    return model_service.update_model(model_id, model_data)

@router.delete("/models/{model_id}")
async def delete_model(
    model_id: str,
    token: dict = Depends(verify_token),
    model_service: ModelService = Depends(get_model_service)
):
    model_service.delete_model(model_id)
    return {"message": "Model deleted successfully"} 