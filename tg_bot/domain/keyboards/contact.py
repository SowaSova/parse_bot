from aiogram.types import (
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_contact_keyboard():
    kkb = ReplyKeyboardBuilder()
    kkb.row(KeyboardButton(text="👥 Отправить контакт", request_contact=True))
    return kkb.as_markup(resize_keyboard=True, one_time_keyboard=True)
