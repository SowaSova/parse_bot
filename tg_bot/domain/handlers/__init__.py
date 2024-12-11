from aiogram import Dispatcher

from .control import router as control_router
from .pagination import router as pagination_router


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        control_router,
        pagination_router,
    )
