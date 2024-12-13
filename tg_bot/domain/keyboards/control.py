from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_back_button_markup_or_builder(entity: str, builder: bool = False):
    """
    Получить клавиатуру с кнопкой назад, или билдер для встраивания в клавиатуру.
    Ловим в хэндлере handlers/control.py

    entity: str - для формирования callback_data, например "main"
    """
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="↩️ Назад", callback_data=f"back_to_{entity}"))
    return kb.as_markup() if not builder else kb


# def get_back_button_builder(entity: str):
#     builder = InlineKeyboardBuilder()
#     builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data=f"back_to_{entity}"))
#     return builder
