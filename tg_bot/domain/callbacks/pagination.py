from typing import Optional

from aiogram.filters.callback_data import CallbackData


class PaginationCallback(CallbackData, prefix="pag"):
    paginator_id: str
    action: str
    page: int
