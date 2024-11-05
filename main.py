from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import hello, prompts, users, chat
from app.core.database import engine
from app.repositories import models
from app.middleware.access_log import access_log_middleware

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

# 设置日志
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
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

# 添加访问日志中间件
app.middleware("http")(access_log_middleware)

# 包含路由
app.include_router(hello.router, prefix=settings.API_V1_STR) 
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(prompts.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下启用热重载
        access_log=False
    )