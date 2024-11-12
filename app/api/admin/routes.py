from fastapi import APIRouter

from app.api.admin.v1.endpoints import admin_users, prompts, accounts, account_tokens, models

router = APIRouter()

router.include_router(admin_users.router, tags=["Admin Users"])
router.include_router(prompts.router, tags=["Prompts"])
router.include_router(accounts.router, tags=["Accounts"])
router.include_router(account_tokens.router, tags=["Account Tokens"])
router.include_router(models.router, tags=["Models"])