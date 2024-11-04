from fastapi import APIRouter
import platform
import os

router = APIRouter()

@router.get("/hello")
async def hello():
    return "hello"

@router.get("/serverInfo")
async def get_server_info():
    server_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.architecture(),
        "hostname": platform.node(),
        "cpu": os.cpu_count(),
    }
    return server_info