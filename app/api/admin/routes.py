from fastapi import APIRouter

from app.api.admin.v1.endpoints import (
    admin_users, dict_groups, dicts, prompts,
    accounts, account_tokens, models, model_providers,
    model_pool, bots, bot_pool
)

router = APIRouter()

router.include_router(admin_users.router, tags=["🔴 Admin Users"])
router.include_router(accounts.router, tags=["🟢 Accounts"])
router.include_router(account_tokens.router, tags=["🔑 Account Tokens"])
router.include_router(dict_groups.router, tags=["📚 Dict Groups"])
router.include_router(dicts.router, tags=["📙 Dict"])
router.include_router(prompts.router, tags=["📝 Prompts"])
router.include_router(model_providers.router, tags=["🎭 Model Providers"])
router.include_router(models.router, tags=["🐣 Models"])
router.include_router(model_pool.router, tags=["🐣🐣 Model Pool"])
router.include_router(bots.router, tags=["😼 Bots"])
router.include_router(bot_pool.router, tags=["😼😼 Bot Pool"])
