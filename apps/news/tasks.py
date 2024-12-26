import logging
import random
import time

from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from celery.signals import worker_ready
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.news.helpers import calculate_post_times
from apps.news.scrapers import (
    fetch_full_news_html,
    fetch_news_list_as_json,
    login_cbonds,
    parse_full_news,
)
from config.constants import NEWS_INTERVAL

from .models import NewsChannel, NewsFilter, PendingNews

logger = logging.getLogger(__name__)


@shared_task
@worker_ready.connect
def parse_news_task(**kwargs):
    news_list = parse_news_list()
    if not news_list:
        logger.info("Нет данных для парсинга.")
        return
    news_list.sort(key=lambda n: n["id"], reverse=False)

    existing_ids = set(PendingNews.objects.values_list("news_id", flat=True))
    new_news = [item for item in news_list if item["id"] not in existing_ids]
    logger.info(
        f"Существующие ID: {existing_ids};\n news_list_id: {news_list} \n new_news: {new_news}"
    )

    if not new_news:
        logger.info("Нет новых новостей.")
        return

    # Генерируем список времени (раскидаем их на 60 минут)
    post_times = calculate_post_times(
        new_news, base_time=timezone.now(), interval_minutes=NEWS_INTERVAL
    )

    # Создаём объекты bulk_create
    data_for_bulk = []
    for item, pt in zip(new_news, post_times):
        data_for_bulk.append(
            PendingNews(
                news_id=item["id"],
                title=item["title"],
                url=item["url"],
                posted=False,  # если нужно выставлять явно
                post_time=pt,
            )
        )
    PendingNews.objects.bulk_create(data_for_bulk)


@shared_task
def post_scheduled_news_task():
    """
    1) Берёт все PendingNews с posted=False,
       у которых post_time <= now
    2) Отправляет их в канал
    3) Ставит posted=True
    """
    from django.utils import timezone

    now = timezone.now()
    qs = PendingNews.objects.filter(posted=False, post_time__lte=now)
    if qs:
        for news in qs:
            # достаём полный HTML и парсим
            html = fetch_full_news_html(news.url)
            full_text = parse_full_news(html)

            # отправляем
            async_to_sync(send_news_to_channel)(news.title, full_text)

            # помечаем как posted
            news.posted = True
            news.save()
    else:
        logger.info("Нет новостей для отправки.")


def parse_news_list():
    """
    Запускаем основную логику парсинга:
      - Узнаём URL
      - Получаем список новостей (JSON-список словарей) через Botasaurus
      - Определяем, какие новости новые (id > last_sent_id)
      - Сохраняем новые в PendingNews с запланированным временем выхода
      - (Не отправляем сразу!)
    """

    # 1. Берём URL из кэша/модели
    url = cache.get("news_filter_url")
    if not url:
        news_filter = NewsFilter.load()
        url = news_filter.url
        cache.set("news_filter_url", url, None)

    if not url:
        logger.warning("Нет URL для парсинга новостей.")
        return

    time.sleep(random.uniform(1, 4))
    news_list = fetch_news_list_as_json(url)
    if not news_list:
        logger.warning("news_list пуст.")
        return

    return news_list


async def send_news_to_channel(title, text):
    from aiogram import Bot, html
    from aiogram.enums import ParseMode

    from apps.news.helpers import html_to_telegram_text

    text = html_to_telegram_text(text)
    msg = f"{html.bold(title)}\n\n{text}"
    bot = Bot(token=settings.BOT_TOKEN)
    channel = await sync_to_async(NewsChannel.load)()
    channel_id = channel.tg_id
    await bot.send_message(chat_id=channel_id, text=msg, parse_mode=ParseMode.HTML)
    logging.info(f"Sent news to channel: {channel_id}")
