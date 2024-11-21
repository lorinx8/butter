from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from app.core.config import settings
from app.repositories import models
from app.core.logging import logger
from sqlalchemy import inspect


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


async def init_db():
    """初始化数据库，创建所有表（如果不存在）"""
    logger.info("开始检查数据库表...")

    async with async_engine.begin() as conn:
        # 正确使用 run_sync 来获取表名
        existing_tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

        # 获取所有模型定义的表名
        model_tables = models.Base.metadata.tables.keys()

        # 检查每个表
        for table_name in model_tables:
            if table_name in existing_tables:
                logger.info(f"表 {table_name} 已存在，跳过")
            else:
                logger.info(f"表 {table_name} 不存在，创建")

        # 创建不存在的表
        await conn.run_sync(
            lambda sync_conn: models.Base.metadata.create_all(
                sync_conn, checkfirst=True)
        )

    logger.info("数据库表检查完成")
