from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import users
from app.core.database import engine
from app.repositories import models

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

# 设置日志
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 确保数据库目录存在
    db_path = Path("./data")
    db_path.mkdir(parents=True, exist_ok=True)
    # Startup
    logger.info("Application startup")
    yield
    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 包含路由
app.include_router(users.router, prefix=settings.API_V1_STR)