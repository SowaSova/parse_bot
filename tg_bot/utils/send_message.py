import asyncio

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings


async def async_send_message(
    chat_id: int, text: str, reply_markup=None, photo_url=None
):
    async with Bot(token=settings.BOT_TOKEN) as bot:
        if photo_url:
            # Отправляем как фото с подписью
            media = FSInputFile(photo_url)
            await bot.send_photo(
                chat_id,
                photo=media,
                caption=text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id, text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
            )


def send_message(chat_id: int, text: str, photo_url=None):
    async_to_sync(async_send_message(chat_id, text, photo_url=photo_url))


def send_message_with_button(chat_id: int, text: str, button: dict, photo_url=None):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=button["text"], url=button["url"])]]
    )
    async_to_sync(
        async_send_message(chat_id, text, reply_markup=markup, photo_url=photo_url)
    )
