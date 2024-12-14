from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.schemas.error_code import ErrorCode
from app.core.schemas.response import error_response
from app.core.logging import logger

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """处理HTTP异常"""  
    logger.error(f"Exception: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="HTTP Server Exception"
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Unhandled exception"
        )
    )
