import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.docs.templates import ElementsHtml
from app.core.exceptions.butter_exception import ButterException
from app.core.exceptions.handlers import http_exception_handler, general_exception_handler, business_exception_handler
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.admin import routes as admin_routes
from app.api.app import routes as app_routes
from app.api.common import routes as common_routes
from app.core.database.db_base import init_db
from app.core.middleware.access_log import access_log_middleware
from app.modules.bot.business.bot_manager import BotManager
from app.modules.llm.business.model_manager import ModelManager

env = os.getenv("ENV")
force_docs = bool(os.getenv("FORCE_DOCS"))
env_is_production = env != "local"

# 检查数据库配置
settings.check_database_config()

# 设置日志
logger = setup_logging()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Startup
    logger.info("[main] Application startup.")
    logger.info("[main] Init db...")
    await init_db()

    # 初始化池
    logger.info("[main] Init model manager...")
    await ModelManager.initialize()
    logger.info("[main] Init bot manager...")
    await BotManager.initialize()

    yield

    # Shutdown
    await ModelManager.cleanup()
    await BotManager.cleanup()
    logger.info("Application shutdown")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json" if not env_is_production or force_docs else None
)

# 添加异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(FastAPIHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(ButterException, business_exception_handler)

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
app.include_router(app_routes.router, prefix=settings.APP_API_V1_STR)
app.include_router(common_routes.router, prefix=settings.COMMON_API_V1_STR)

if not env_is_production or force_docs:
    @app.get("/docs", response_class=HTMLResponse)
    async def api_docs():
        return ElementsHtml.BASIC


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.UVICORN_PORT,
        reload=True,  # 开发模式下启用热重载
        access_log=False
    )
