from asgiref.sync import sync_to_async

from apps.users.models import TelegramUser


@sync_to_async
def get_or_create_user(telegram_id: int, tg_username: str = None):
    return TelegramUser.objects.get_or_create(
        telegram_id=telegram_id, tg_username=tg_username
    )


@sync_to_async
def update_user(
    telegram_id: int,
    tg_username: str = None,
    full_name: str = None,
    phone_number: str = None,
):
    return TelegramUser.objects.filter(telegram_id=telegram_id).update(
        tg_username=tg_username,
        full_name=full_name,
        phone_number=phone_number,
        registred=True,
    )
