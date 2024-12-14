from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.security import verify_token
from app.core.database.db_base import get_db
from app.core.schemas.error_code import ErrorCode
from app.core.schemas.response import success_response, error_response
from app.modules.bot.business.bot_manager import BotManager
from app.modules.bot.repositories import BotRepository
from app.modules.bot.schemas import BotStandardCreate, BotUpdate
from app.modules.bot.services import BotService

router = APIRouter()


def get_bot_service(db: Session = Depends(get_db)):
    return BotService(BotRepository(db))


async def get_bot_manager():
    return await BotManager.get_instance()


@router.post("/bots-standard")
async def create_bot_standard(
    bot_data: BotStandardCreate,
    _: dict = Depends(verify_token),
    bot_manager: BotManager = Depends(get_bot_manager)
):
    try:
        bot = bot_manager.create_standard_bot(bot_data)
        return success_response(data=bot, message="Bot created successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/bots")
async def get_bots(
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(verify_token),
    bot_service: BotService = Depends(get_bot_service)
):
    try:
        bots = bot_service.get_bots(skip=skip, limit=limit)
        return success_response(data=bots)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/bots/{bot_id}")
async def get_bot(
    bot_id: str,
    _: dict = Depends(verify_token),
    bot_service: BotService = Depends(get_bot_service)
):
    try:
        bot = bot_service.get_bot(bot_id)
        return success_response(data=bot)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.put("/bots/{bot_id}")
async def update_bot(
    bot_id: str,
    bot_data: BotUpdate,
    _: dict = Depends(verify_token),
    bot_service: BotService = Depends(get_bot_service)
):
    try:
        bot = bot_service.update_bot(bot_id, bot_data)
        return success_response(data=bot, message="Bot updated successfully")
    except ValueError as e:
        return error_response(ErrorCode.INVALID_PARAMS, str(e))
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.delete("/bots/{bot_id}")
async def delete_bot(
    bot_id: str,
    _: dict = Depends(verify_token),
    bot_service: BotService = Depends(get_bot_service)
):
    try:
        bot_service.delete_bot(bot_id)
        return success_response(message="Bot deleted successfully")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
