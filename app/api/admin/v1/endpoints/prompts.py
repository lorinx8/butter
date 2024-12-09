from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.response import success_response, error_response
from app.core.error_code import ErrorCode
from app.repositories.prompt_repository import PromptRepository
from app.services.prompt_service import PromptService
from app.schemas.prompt import PromptCreate, PromptUpdate

router = APIRouter()


def get_prompt_service(db: Session = Depends(get_db)):
    return PromptService(PromptRepository(db))


@router.post("/prompts")
async def create_prompt(
    prompt_data: PromptCreate,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    try:
        prompt = prompt_service.create_prompt(prompt_data)
        return success_response(data=prompt, message="Prompt created successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/prompts")
async def get_prompts(
    skip: int = 0,
    limit: int = 100,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    try:
        prompts = prompt_service.get_prompts(skip=skip, limit=limit)
        return success_response(data=prompts)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/prompts/{prompt_id}")
async def get_prompt(
    prompt_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    try:
        prompt = prompt_service.get_prompt(prompt_id)
        if not prompt:
            return error_response(ErrorCode.NOT_FOUND, f"Prompt {prompt_id} not found")
        return success_response(data=prompt)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: str,
    prompt_data: PromptUpdate,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    try:
        prompt = prompt_service.update_prompt(prompt_id, prompt_data)
        if not prompt:
            return error_response(ErrorCode.NOT_FOUND, f"Prompt {prompt_id} not found")
        return success_response(data=prompt, message="Prompt updated successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    prompt_service: PromptService = Depends(get_prompt_service)
):
    try:
        prompt_service.delete_prompt(prompt_id)
        return success_response(message="Prompt deleted successfully")
    except ValueError as e:
        return error_response(ErrorCode.NOT_FOUND, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
