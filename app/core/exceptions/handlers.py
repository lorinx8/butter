from fastapi import Request, HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.schemas.error_code import ErrorCode
from app.core.schemas.response import error_response
from app.core.logging import logger
from typing import Union
from app.core.exceptions.butter_exception import ButterException

async def business_exception_handler(request: Request, exc: ButterException) -> JSONResponse:
    """处理业务异常"""
    logger.error(f"Business Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_code=exc.error_code,
            message=exc.message
        )
    )

async def http_exception_handler(request: Request, exc: Union[StarletteHTTPException, FastAPIHTTPException]) -> JSONResponse:
    """处理HTTP异常"""
    logger.error(f"HTTP Exception: {exc.detail if hasattr(exc, 'detail') else str(exc)}")
    
    # 根据状态码映射到对应的错误码
    error_code = ErrorCode.INTERNAL_SERVER_ERROR
    if exc.status_code == 404:
        error_code = ErrorCode.NOT_FOUND
    elif exc.status_code == 400:
        error_code = ErrorCode.INVALID_PARAMS
    elif exc.status_code == 401:
        error_code = ErrorCode.UNAUTHORIZED
    elif exc.status_code == 403:
        error_code = ErrorCode.FORBIDDEN
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            error_code=error_code,
            message=exc.detail if hasattr(exc, 'detail') else str(exc)
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常"""
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=error_response(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=str(exc)
        )
    )
