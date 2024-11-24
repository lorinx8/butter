from fastapi import APIRouter
from app.api.app.v1.routes import router as app_router
from app.api.admin.v1.routes import router as admin_router

api_router = APIRouter()

# Include app and admin routers
api_router.include_router(app_router, prefix="/v1")
api_router.include_router(admin_router, prefix="/v1")
