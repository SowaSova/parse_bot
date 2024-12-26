from typing import Optional

from aiogram.filters.callback_data import CallbackData


class LotteryCallback(CallbackData, prefix="participate"):
    id: int
