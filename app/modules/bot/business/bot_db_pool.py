from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager

from app.core.config import settings


class BotDatabasePool:
    _instance = None
    _pool = None

    @classmethod
    async def get_pool(cls):
        if cls._pool is None:
            cls._pool = AsyncConnectionPool(
                conninfo=settings.DATABASE_URI,
                max_size=20,  # 根据需求调整
                open=False,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0,
                }
            )
            await cls._pool.open()
        return cls._pool

    @classmethod
    @asynccontextmanager
    async def get_connection(cls):
        pool = await cls.get_pool()
        async with pool.connection() as conn:
            yield conn

    @classmethod
    async def close_pool(cls):
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
