from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from app.core.config import settings


# 同步引擎
engine = create_engine(
    settings.DATABASE_URL_PSYCOPG,
    pool_size=5,
    max_overflow=10
)

# 异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL_PSYCOPG,
    pool_size=5,
    max_overflow=10
)

# 同步 Session
SessionLocal = sessionmaker(engine)

# 异步 Session
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 同步依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 异步依赖
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
