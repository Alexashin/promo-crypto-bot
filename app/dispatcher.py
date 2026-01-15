from __future__ import annotations

from aiogram import Dispatcher
from app.db.session import SessionFactory
from app.middlewares.db import DBSessionMiddleware
from app.middlewares.user_context import UserContextMiddleware
from app.routers.errors import router as errors_router
from app.routers.user_start import router as user_start_router
from app.routers.user_callbacks import router as user_callbacks_router
from app.routers.user_menu import router as user_menu_router
from app.routers.admin import router as admin_router
from app.routers.admin_settings import router as admin_settings_router
from app.routers.admin_templates import router as admin_templates_router


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    # порядок важен: сначала db, потом user
    dp.update.middleware(DBSessionMiddleware(SessionFactory))
    dp.update.middleware(UserContextMiddleware())

    dp.include_router(errors_router)
    dp.include_router(user_start_router)
    dp.include_router(user_callbacks_router)
    dp.include_router(user_menu_router)
    dp.include_router(admin_router)
    dp.include_router(admin_settings_router)
    dp.include_router(admin_templates_router)

    return dp
