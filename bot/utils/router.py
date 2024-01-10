from bot.handlers.start.router import router as start_router
from bot.handlers.ai.router import router as ai_router
from bot.handlers.error.router import router as error_router

from aiogram import Dispatcher


def setup_routers(dp: Dispatcher):
    dp.include_routers(
        ai_router,
        start_router,
        error_router
    )
