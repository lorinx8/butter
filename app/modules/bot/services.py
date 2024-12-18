from typing import List

from fastapi import HTTPException

from app.core.utils import code_generator
from app.modules.bot.models import Bot
from app.modules.bot.repositories import BotRepository
from app.modules.bot.schemas import BotStandardCreate, BotUpdate


class BotService:
    def __init__(self, bot_repository: BotRepository):
        self.bot_repository = bot_repository

    def get_all(self) -> List[Bot]:
        return self.bot_repository.get_all()

    def create_bot(self, bot_data: BotStandardCreate) -> Bot:
        # 检查code是否已存在
        if (not bot_data.code and not len(bot_data.code) == 0) and self.bot_repository.get_by_code(bot_data.code):
            raise HTTPException(
                status_code=400, detail="Bot code already exists")

        # 验证bot_type
        if bot_data.bot_type not in ["standard", "customized"]:
            raise HTTPException(
                status_code=400, detail="Invalid bot type")

        if not bot_data.code:
            bot_data.code = code_generator.generate_code("bot")

        return self.bot_repository.create(
            code=bot_data.code,
            name=bot_data.name,
            bot_type=bot_data.bot_type,
            properties=bot_data.properties.model_dump(),
            description=bot_data.description,
            version=bot_data.version
        )

    def get_bot(self, bot_id: str) -> Bot:
        bot = self.bot_repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        return bot

    def get_bot_by_code(self, bot_code: str) -> Bot:
        bot = self.bot_repository.get_by_code(bot_code)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        return bot

    def get_bots(self, skip: int = 0, limit: int = 100) -> List[Bot]:
        return self.bot_repository.get_all(skip=skip, limit=limit)

    def update_bot(self, bot_id: str, bot_data: BotUpdate) -> Bot:
        bot = self.bot_repository.get_by_id(bot_id)
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        update_data = bot_data.model_dump(exclude_unset=True)
        if "bot_type" in update_data and update_data["bot_type"] not in ["standard", "customized"]:
            raise HTTPException(status_code=400, detail="Invalid bot type")

        return self.bot_repository.update(bot_id, **update_data)

    def delete_bot(self, bot_id: str) -> bool:
        if not self.bot_repository.delete(bot_id):
            raise HTTPException(status_code=404, detail="Bot not found")
        return True
