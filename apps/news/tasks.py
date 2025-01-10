import logging
import random
import time

from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from celery.signals import worker_ready
from celery_once import QueueOnce
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.news.api_parse import parse_news_list_by_filters
from apps.news.exceptions import InvalidOTPError
from apps.news.helpers import calculate_post_times
from apps.news.scrapers import (
    fetch_full_news_html,
    fetch_news_list_as_json,
    login_cbonds,
    parse_full_news,
)
from config.constants import NEWS_INTERVAL
from tg_bot.utils import async_send_message, send_message

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
    qs = PendingNews.objects.filter(posted=False, post_time__lte=now).first()
    if qs:
        # достаём полный HTML и парсим
        html = fetch_full_news_html(qs.url)
        full_text = parse_full_news(html)

        # отправляем
        async_to_sync(send_news_to_channel)(qs.title, full_text)

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

    # 1) Если флаг is_url => парсим по ссылке
    if news_filter:
        url = cache.get("news_filter_url")  # берем из кэша
        if not url:
            # fallback, вдруг в кэше нет
            url = news_filter.url

        if not url:
            logger.warning("is_url=True, но нет URL. Остановка парсинга.")
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

    # 2) Если is_url=False => POST к cbounds.ru с фильтрами (берем param_value из кэша)
    else:
        # Собираем списки из кэша (или проверяем fallback)
        region_values = cache.get("news_filter_region_values") or []
        country_values = cache.get("news_filter_country_values") or []
        type_values = cache.get("news_filter_type_values") or []
        theme_values = cache.get("news_filter_theme_values") or []

        # Проверяем, что что-то вообще есть
        if not (region_values or country_values or type_values or theme_values):
            logger.warning("is_url=False, но нет ни одного фильтра в кэше.")
            # Можно вернуть пустой список, чтобы парсинг не падал
            return []

        return parse_news_list_by_filters(
            region_values=region_values,
            country_values=country_values,
            type_values=type_values,
            theme_values=theme_values,
        )


async def send_news_to_channel(title, text):
    from aiogram import Bot, html
    from aiogram.enums import ParseMode

    from apps.news.helpers import html_to_telegram_text

    text = html_to_telegram_text(text)
    msg = f"{html.bold(title)}\n\n{text}"
    channel = await sync_to_async(NewsChannel.load)()
    channel_id = channel.tg_id
    send_message(channel_id, msg)
    logging.info(f"Sent news to channel: {channel_id}")
