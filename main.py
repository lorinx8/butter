from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.admin import routes as admin_routes
from app.api.common import routes as common_routes
from app.core.database import engine
from app.repositories import models
from app.middleware.access_log import access_log_middleware

# 检查数据库配置
settings.check_database_config()

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
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# 添加访问日志中间件
app.middleware("http")(access_log_middleware)

# 包含路由
app.include_router(admin_routes.router, prefix=settings.ADMIN_API_V1_STR)
app.include_router(common_routes.router, prefix=settings.COMMON_API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 开发模式下启用热重载
        access_log=False
    )
