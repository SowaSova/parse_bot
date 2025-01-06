import logging
import random
import time

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)


def parse_news_list_by_filters(
    region_values=None,
    country_values=None,
    type_values=None,
    theme_values=None,
):
    """
    Формируем POST-запрос к https://cbounds.ru/api/news/ исходя из
    param_value-фильтров (region, country, type, theme), которые мы взяли из кэша.
    """
    region_values = region_values or []
    country_values = country_values or []
    type_values = type_values or []
    theme_values = theme_values or []

    payload = {
        "filters": [
            {"field": "show_only_loans", "operator": "eq", "value": 0},
            # При необходимости можно добавить фильтр по дате:
            {
                "field": "date",
                "operator": "ge",
                "value": str(timezone.localdate().isoformat()),  # YYYY-MM-DD
            },
        ],
        "sorting": [],
        "quantity": {"offset": 0, "limit": 30, "page": 1},
        "lang": "rus",
    }

    if region_values:
        payload["filters"].append(
            {
                "field": "subregion_id",
                "operator": "in",
                "value": [str(x) for x in region_values],
            }
        )

    if country_values:
        payload["filters"].append(
            {
                "field": "country_id",
                "operator": "in",
                "value": [str(x) for x in country_values],
            }
        )

    if type_values:
        payload["filters"].append(
            {"field": "type", "operator": "in", "value": [str(x) for x in type_values]}
        )

    if theme_values:
        payload["filters"].append(
            {
                "field": "section_id",
                "operator": "in",
                "value": [str(x) for x in theme_values],
            }
        )

    logger.info(f"Отправляем POST на cbonds.ru с payload: {payload}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://cbonds.ru/news/",  # иногда нужно, если сайт проверяет реферер
    }
    cookies = {"CBONDSSESSID": "9po9dcitb6j0odllh3r97dfgn8"}

    try:
        time.sleep(random.uniform(1, 3))
        response = requests.post(
            "https://cbonds.ru/api/news/",
            json=payload,
            headers=headers,
            cookies=cookies,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к cbonds.ru: {e}")
        return []

    data = response.json()
    if "data" not in data or "news" not in data["data"]:
        logger.warning("Невалидная структура ответа от cbounds.ru.")
        return []

    raw_news = data["data"]["news"]
    news_list = []
    for item in raw_news:
        news_list.append(
            {
                "title": item.get("caption", ""),  # или другое поле
                "url": item.get("cb_link", ""),  # ссылка на полную новость
                "id": item.get("id", ""),  # уникальный идентификатор
                "time": item.get("time", ""),  # допустим, "10:31"
                # Можете добавить что-то ещё, например "date": item.get("date", "")
            }
        )
    return news_list
