from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .control import get_back_button_or_builder


def get_faq_instruction_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой для доступа к FAQ.

    :return: InlineKeyboardMarkup с кнопкой "FAQ".
    """
    builder = InlineKeyboardBuilder()

    faq_button = InlineKeyboardButton(
        text="🔍 FAQ",
        callback_data="faq_instructions",
    )
    builder.add(faq_button)

    builder.attach(get_back_button_or_builder(entity="main", builder=True))

    return builder.as_markup()
