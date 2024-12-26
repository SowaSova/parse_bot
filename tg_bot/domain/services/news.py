from asgiref.sync import sync_to_async

from apps.news.models import NewsChannel
from config.constants import TG_URL


@sync_to_async
def get_channel_url():
    ch = NewsChannel.load()
    return f"{TG_URL}{ch.tg_username}" or f"{ch.link}"
