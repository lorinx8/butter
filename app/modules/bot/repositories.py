from typing import Optional, List

from sqlalchemy.orm import Session

from app.modules.bot.models import Bot


class BotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, code: str, name: str, bot_type: str,
               properties: Optional[dict] = None,
               description: Optional[str] = None,
               version: Optional[str] = None) -> Bot:
        db_bot = Bot(
            code=code,
            name=name,
            bot_type=bot_type,
            properties=properties,
            description=description,
            version=version
        )
        self.db.add(db_bot)
        self.db.commit()
        self.db.refresh(db_bot)
        return db_bot

    def get_by_id(self, bot_id: str) -> Optional[Bot]:
        return self.db.query(Bot).filter(Bot.id == bot_id).first()

    def get_by_code(self, code: str) -> Optional[Bot]:
        return self.db.query(Bot).filter(Bot.code == code).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Bot]:
        return self.db.query(Bot).offset(skip).limit(limit).all()

    def update(self, bot_id: str, **kwargs) -> Optional[Bot]:
        bot = self.get_by_id(bot_id)
        if bot:
            for key, value in kwargs.items():
                setattr(bot, key, value)
            self.db.commit()
            self.db.refresh(bot)
        return bot

    def delete(self, bot_id: str) -> bool:
        bot = self.get_by_id(bot_id)
        if bot:
            self.db.delete(bot)
            self.db.commit()
            return True
        return False
