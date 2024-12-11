import asyncio
import logging

from aiogram import Bot, exceptions
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from celery import shared_task
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from apps.broadcast.models import BroadcastMessage
from apps.users.models import TelegramUser

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_scheduled_messages(self):
    try:
        asyncio.run(send_broadcast_messages())
    except Exception as exc:
        logger.error(f"Error sending scheduled messages: {exc}")
        raise self.retry(exc=exc)


async def send_broadcast_messages():
    bot = Bot(token=settings.BOT_TOKEN)

    now = timezone.now()
    # Получаем список сообщений асинхронно
    messages_to_send = await sync_to_async(list)(
        BroadcastMessage.objects.filter(
            Q(scheduled_time__lte=now) & Q(is_sent=False)
        )
    )

    if not messages_to_send:
        logger.info("Нет сообщений для отправки")
        await bot.session.close()
        return

    # Получаем список пользователей асинхронно
    users = await sync_to_async(list)(TelegramUser.objects.all())

    for message in messages_to_send:
        for user in users:
            try:
                if message.attachments:
                    file = FSInputFile(message.attachments.path)
                    await bot.send_document(
                        chat_id=user.telegram_id,
                        document=file,
                        caption=message.message_text,
                    )
                else:
                    await bot.send_message(
                        chat_id=user.telegram_id, text=message.message_text
                    )
            except exceptions.TelegramAPIError as e:
                logger.error(
                    f"Ошибка при отправке сообщения пользователю {user.telegram_id}: {e}"
                )
            except Exception as e:
                logger.error(
                    f"Непредвиденная ошибка при отправке сообщения пользователю {user.telegram_id}: {e}"
                )

        message.is_sent = True
        await sync_to_async(message.save)()

    # Закрываем сессию бота
    await bot.session.close()
