from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.repositories.prompt_repository import PromptRepository
from app.services.prompt_service import PromptService
from app.schemas.chat_prompt import ChatPromptCreate, ChatPromptUpdate, ChatPromptInDB

router = APIRouter()

def get_prompt_service(db: Session = Depends(get_db)):
    return PromptService(PromptRepository(db))

@router.post("/prompts/", response_model=ChatPromptInDB)
async def create_prompt(
    prompt_data: ChatPromptCreate,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    return prompt_service.create_prompt(prompt_data)

@router.get("/prompts/", response_model=List[ChatPromptInDB])
async def get_prompts(
    skip: int = 0,
    limit: int = 100,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    return prompt_service.get_prompts(skip=skip, limit=limit)

@router.get("/prompts/{prompt_id}", response_model=ChatPromptInDB)
async def get_prompt(
    prompt_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    return prompt_service.get_prompt(prompt_id)

@router.put("/prompts/{prompt_id}", response_model=ChatPromptInDB)
async def update_prompt(
    prompt_id: str,
    prompt_data: ChatPromptUpdate,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    return prompt_service.update_prompt(prompt_id, prompt_data)

@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    prompt_service.delete_prompt(prompt_id)
    return {"message": "Prompt deleted successfully"}