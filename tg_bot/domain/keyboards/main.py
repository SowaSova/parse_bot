from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tg_bot.domain.services import get_channel_url, get_manager_url


async def get_main_keyboard(channel: bool = False):
    manager = await get_manager_url()
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(text="Купить продукт", callback_data="products"),
        InlineKeyboardButton(text="FAQ", callback_data="faq_instructions"),
        InlineKeyboardButton(text="Связаться с менеджером", url=manager),
    )
    if channel:
        ch_url = await get_channel_url()
        kb.add(InlineKeyboardButton(text="Вернуться в канал", url=ch_url))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
