from aiogram import Dispatcher

from .control import router as control_router
from .faq import router as faq_router
from .lottery import router as lottery_router
from .pagination import router as pagination_router
from .products import router as products_router
from .start import router as start_router


def register_handlers(dp: Dispatcher):
    dp.include_routers(
        control_router,
        pagination_router,
        start_router,
        faq_router,
        products_router,
        lottery_router,
    )
