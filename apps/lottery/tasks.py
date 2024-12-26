import logging
import random

from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from django.conf import settings

from apps.lottery.models import Lottery
from apps.news.models import NewsChannel

logger = logging.getLogger(__name__)


@shared_task
def announce_lottery(lottery_id):
    async def announce(lottery_id):
        lottery = await sync_to_async(Lottery.objects.filter(pk=lottery_id).first)()
        if not lottery:
            logger.info(f"Lottery {lottery_id} not found")
            return

        channel = await sync_to_async(NewsChannel.load)()
        channel_id = channel.tg_id
        bot_username = settings.BOT_USERNAME
        bot = Bot(
            token=settings.BOT_TOKEN,
        )
        start_param = f"lottery_{lottery_id}"

        participation_url = f"https://t.me/{bot_username}?start={start_param}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Участвовать", url=participation_url)]
            ]
        )

        caption_text = (
            f"Новый розыгрыш!\n\n{lottery.title}\n\n{lottery.description or ''}\n"
            f"Окончание: {lottery.fin_date.strftime('%d.%m.%Y %H:%M')}"
        )

        if lottery.photo:
            photo = FSInputFile(lottery.photo.path)
            await bot.send_photo(
                chat_id=channel_id,
                photo=photo,
                caption=caption_text,
                reply_markup=keyboard,
            )
        else:
            await bot.send_message(
                chat_id=channel_id,
                text=caption_text,
                reply_markup=keyboard,
            )

        await bot.session.close()

    async_to_sync(announce)(lottery_id)


@shared_task
def finish_lottery(lottery_id):
    # Просто вызываем асинхронную функцию через async_to_sync
    async_to_sync(finish_lottery_async)(lottery_id)


async def finish_lottery_async(lottery_id):
    lottery = await sync_to_async(Lottery.objects.filter(pk=lottery_id).first)()
    if lottery is None:
        return

    participants = await sync_to_async(list)(lottery.participants.all())
    if lottery.is_finished or len(participants) == 0:
        return

    winner = random.choice(participants)

    # Сохраняем изменения в БД
    await sync_to_async(setattr)(lottery, "winner", winner)
    await sync_to_async(setattr)(lottery, "is_finished", True)
    await sync_to_async(lottery.save)()

    bot = Bot(token=settings.BOT_TOKEN)

    channel = await sync_to_async(NewsChannel.load)()
    channel_id = channel.tg_id

    await bot.send_message(
        chat_id=channel_id,
        text=(
            f"Розыгрыш «{lottery.title}» завершён!\n"
            f"Победитель: {winner.full_name} | {winner.tg_username or winner.telegram_id}\n"
            f"Поздравляем!"
        ),
    )

    await bot.send_message(
        chat_id=winner.telegram_id,
        text=(
            f"Поздравляем! Вы выиграли в розыгрыше «{lottery.title}»!\n"
            f"С вами свяжутся в ближайшее время."
        ),
    )

    await bot.session.close()
