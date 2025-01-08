import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from django.conf import settings


async def async_send_message(
    chat_id: int, text: str, reply_markup=None, photo_url=None
):
    bot = Bot(token=settings.BOT_TOKEN)

    if photo_url:
        # Отправляем как фото с подписью
        media = InputMediaPhoto(media=photo_url, caption=text)
        await bot.send_photo(
            chat_id,
            photo_url,
            caption=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await bot.send_message(
            chat_id, text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )


def send_message(chat_id: int, text: str):
    asyncio.run(async_send_message(chat_id, text))


def send_message_with_button(chat_id: int, text: str, button: dict, photo_url=None):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=button["text"], url=button["url"])]]
    )
    asyncio.run(
        async_send_message(chat_id, text, reply_markup=markup, photo_url=photo_url)
    )
