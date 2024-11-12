from fastapi import APIRouter
from app.api.common.v1.endpoints import hello

router = APIRouter()

router.include_router(hello.router, tags=["Hello for testing"])