import logging
import random
import time

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.signals import worker_ready
from django.core.cache import cache
from django.utils import timezone

from apps.news.exceptions import InvalidOTPError
from apps.news.helpers import calculate_post_times
from apps.news.scrapers import (
    fetch_full_news_html,
    fetch_news_list_as_json,
    parse_full_news,
)
from config.constants import NEWS_INTERVAL
from tg_bot.utils import async_send_message

from .models import NewsChannel, NewsFilter, PendingNews

logger = logging.getLogger(__name__)


@shared_task
def remove_sended_news_task():
    PendingNews.objects.filter(posted=True).delete()
    logger.info("Удалены отправленные новости.")
    return


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
    qs = PendingNews.objects.filter(posted=False, post_time__lte=now).first()
    if qs:
        # достаём полный HTML и парсим
        html = fetch_full_news_html(qs.url)
        full_text = parse_full_news(html)

        # отправляем
        send_news_to_channel(qs.title, full_text)

        # помечаем как posted
        qs.posted = True
        qs.save()
    else:
        logger.info("Нет новостей для отправки.")


def parse_news_list():
    """
    Запускаем основную логику парсинга:
      - Если news_filter.is_url=True, берем url из кэша
      - Иначе берём M2M-параметры (уже из кэша) и делаем POST-запрос к cbounds.ru
    """
    news_filter = NewsFilter.load()
    if not news_filter:
        logger.warning("Нет фильтра. Остановка парсинга.")
        return []
    url = cache.get("news_filter_url")  # берем из кэша
    if not url:
        # fallback, вдруг в кэше нет
        url = news_filter.url

    if not url:
        logger.warning("Нет URL. Остановка парсинга.")
        return []

    # Делаем старый fetch
    time.sleep(random.uniform(1, 3))
    news_list = []
    try:
        news_list = fetch_news_list_as_json(url)
        return news_list
    except InvalidOTPError:
        logger.warning("Неверный OTP.")
        return []


def send_news_to_channel(title, text):
    from aiogram import html

    from apps.news.helpers import html_to_telegram_text

    text = html_to_telegram_text(text)
    msg = f"{html.bold(title)}\n\n{text}"
    channel = NewsChannel.load()
    channel_id = channel.tg_id
    async_to_sync(async_send_message)(channel_id, msg)
    logging.info(f"Sent news to channel: {channel_id}")
