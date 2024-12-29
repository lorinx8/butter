from fastapi import APIRouter
import platform
import os

from app.core.exceptions.error_code import ErrorCode
from app.core.schemas.response import success_response, error_response

router = APIRouter()


@router.get("/hello-echo/{message}")
async def hello_echo(message: str):
    try:
        return success_response(data=f"echo: {message}")
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))


@router.get("/server-info")
async def get_server_info():
    try:
        server_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture(),
            "hostname": platform.node(),
            "cpu": os.cpu_count(),
        }
        return success_response(data=server_info)
    except Exception as e:
        return error_response(ErrorCode.UNKNOWN_ERROR, str(e))
