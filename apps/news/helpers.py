import logging
import math
import re
from datetime import timedelta

from config.constants import NEWS_INTERVAL

logger = logging.getLogger(__name__)


def calculate_post_times(new_news, base_time, interval_minutes=NEWS_INTERVAL):
    """
    Возвращает список post_time для каждой новости,
    чтобы равномерно "размазать" их по interval_minutes.
    """
    count = len(new_news)
    step = math.ceil(interval_minutes / count)
    post_times = []
    for index in range(count):
        offset = index * step
        if offset >= interval_minutes:
            offset = interval_minutes - 1
        post_time = base_time + timedelta(minutes=offset)
        post_times.append(post_time)
    return post_times


def extract_news_id(url: str) -> int:
    """
    Извлекает числовой ID новости из ссылки вида https://cbonds.ru/news/3213355/

    :param url: URL новости
    :return: int ID новости (или 0, если не получилось извлечь)
    """
    match = re.search(r"/news/(\d+)/", url)
    return int(match.group(1)) if match else 0


def html_to_telegram_text(raw_html: str) -> str:
    """
    Преобразует HTML (с тегами <p>, <br>, <li>, <b>, <i>, ...) в текст,
    пригодный для отправки в Telegram с parse_mode="HTML".

    - <p> -> \n\n
    - <br> -> \n
    - <li> -> "\n- "
    - <strong> -> <b>
    - <em> -> <i>
    - Удаляем все прочие теги и лишние пустые строки.
    """
    import re

    text = raw_html

    # 1. <br> => \n
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)

    # 2. <p> => \n\n
    text = re.sub(r"(?i)</?p[^>]*>", "\n\n", text)

    # 3. <li> => "\n- ", </li> => ""
    text = re.sub(r"(?i)<li[^>]*>", "\n- ", text)
    text = re.sub(r"(?i)</li>", "", text)

    # 4. <td>, <tr>, <div>, <span>, <section> -> \n
    for tag in ("td", "tr", "div", "span", "section"):
        text = re.sub(rf"(?i)</?{tag}[^>]*>", "\n", text)

    # 5. Заменяем <strong> -> <b>, <em> -> <i>
    text = re.sub(r"(?i)<strong>(.*?)</strong>", r"<b>\1</b>", text)
    text = re.sub(r"(?i)<em>(.*?)</em>", r"<i>\1</i>", text)

    # 6. Удаляем все прочие теги (<script>, <style>, <a> и т. д.)
    text = re.sub(r"(?s)<[^>]*>", "", text)

    # 7. Сжимаем лишние пустые строки (не более двойных \n)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
