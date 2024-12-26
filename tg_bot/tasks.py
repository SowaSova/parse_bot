import logging

from aiogram import Bot, exceptions
from aiogram.types import FSInputFile
from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.broadcast.models import BroadcastMessage
from apps.users.models import TelegramUser

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_broadcast_message_task(self, broadcast_message_id: int):
    """
    Celery-задача, отправляющая конкретное сообщение с заданным ID.
    """
    try:
        async_to_sync(send_broadcast_message)(broadcast_message_id)
    except Exception as exc:
        logger.error(f"Error sending broadcast message: {exc}")
        raise self.retry(exc=exc)


async def send_broadcast_message(broadcast_message_id: int):
    """
    Асинхронная часть отправки конкретного сообщения.
    """
    bot = Bot(token=settings.BOT_TOKEN)

    # Получаем сообщение
    message = await sync_to_async(BroadcastMessage.objects.get)(pk=broadcast_message_id)

    # Проверяем, не отправлено ли оно уже
    if message.is_sent:
        logger.info(f"Сообщение {broadcast_message_id} уже отмечено как отправленное.")
        await bot.session.close()
        return

    # Если время плановой отправки в будущем - просто выходим.
    # (В теории, такое произойти не должно, тк Celery запустит задачу не раньше времени.
    # Но на всякий случай подстрахуемся.)
    now = timezone.now()
    if message.scheduled_time and message.scheduled_time > now:
        logger.info(
            f"Время отправки сообщения {broadcast_message_id} ещё не наступило. "
            "Задача выполнится позже."
        )
        await bot.session.close()
        return

    # Получаем список пользователей
    users = await sync_to_async(list)(TelegramUser.objects.all())

    # Рассылаем
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

    # Выставляем флаг «отправлено»
    message.is_sent = True
    await sync_to_async(message.save)()

    # await bot.session.close()
