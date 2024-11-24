from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.managers.llm.model_pool import ModelPool
from app.core.exception_handlers import http_exception_handler, general_exception_handler
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.admin import routes as admin_routes
from app.api.common import routes as common_routes
from app.core.database import init_db
from app.middleware.access_log import access_log_middleware


# 检查数据库配置
settings.check_database_config()

# 设置日志
logger = setup_logging()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Startup
    logger.info("Application startup")
    await init_db()
    await ModelPool.initialize()

    yield

    # Shutdown
    await ModelPool.cleanup()
    logger.info("Application shutdown")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 添加异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境建议设置具体的源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
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
        port=settings.UVICORN_PORT,
        reload=False,  # 开发模式下启用热重载
        access_log=False
    )
