import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.broadcast.models import BroadcastMessage
from tg_bot.tasks import send_broadcast_message_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BroadcastMessage)
def schedule_broadcast_message(sender, instance, created, **kwargs):
    """
    Сигнал, который при сохранении BroadcastMessage решает,
    когда именно вызвать задачу на отправку.
    """
    # Если сообщение уже отправлено – ничего не делаем
    if instance.is_sent:
        return

    now = timezone.now()
    scheduled_time = instance.scheduled_time

    # Если время не указано (None) — отправляем сразу
    if scheduled_time is None:
        # Но отправляем только при создании,
        # чтобы при повторном сохранении не отправлялись дубли
        if created:
            send_broadcast_message_task.delay(instance.id)
            logger.info(
                f"Задача на немедленную отправку сообщения {instance.id}, "
                f"так как время не указано (scheduled_time=None)."
            )
        return

    # Если дата есть, но уже в прошлом — тоже отправляем немедленно
    if scheduled_time <= now:
        # Отправить сразу
        send_broadcast_message_task.delay(instance.id)
        logger.info(
            f"Задача на немедленную отправку сообщения {instance.id}, "
            f"так как указанное время ({scheduled_time}) уже прошло."
        )
    else:
        # Иначе планируем по ETA
        send_broadcast_message_task.apply_async((instance.id,), eta=scheduled_time)
        logger.info(
            f"Задача на отправку сообщения {instance.id} запланирована на {scheduled_time}."
        )
