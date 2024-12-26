from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.conf import settings

from tg_bot.domain.callbacks import LotteryCallback


def generate_participation_button(lottery_id):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Участвовать",
                    callback_data=LotteryCallback(id=lottery_id).pack(),
                )
            ]
        ],
    )
    return kb


def get_bot_keyboard():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Получить бота",
                    url=f"https://t.me/@{settings.BOT_USERNAME}",
                )
            ]
        ],
    )
    return kb
