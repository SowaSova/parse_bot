import logging
import random
import time

import cloudscraper
from botasaurus.browser import Driver, NotFoundException, Wait, browser
from django.conf import settings

from apps.news.exceptions import InvalidOTPError
from apps.news.helpers import extract_news_id, notify_admins_invalid_otp

from .models import OTP

logger = logging.getLogger(__name__)


def fetch_full_news_html(url: str) -> str:
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False},
    )
    time.sleep(random.uniform(1, 3))
    response = scraper.get(url)
    return response.text


def parse_full_news(html: str) -> str:
    """
    1. Ищем var newsInfo = {...};
    2. Достаём "text" из JSON.
    3. Ограничиваем до 3 абзацев.
    4. Ограничиваем итог до 4096 символов.
    """
    import json
    import re

    match = re.search(r"var newsInfo\s*=\s*(.*?);", html, re.DOTALL)
    if not match:
        return ""
    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        return ""

    # Основной текст новости
    text = data.get("text", "")
    if not text:
        return ""

    # 1) Разбиваем по переводам строк, убираем пустые
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    # 2) Берём первые 3 абзаца
    paragraphs = paragraphs[:3]
    # 3) Склеиваем их через двойной перенос строки (например)
    clipped_text = "\n\n".join(paragraphs)
    # 4) Ограничиваем итоговый текст длиной 4096 символов
    if len(clipped_text) > 4000:
        clipped_text = clipped_text[:4000]

    return clipped_text


# @browser(
#     cache=True,
#     max_retry=5,  # Retry up to 5 times, which is a good default
#     reuse_driver=True,  # Reuse the same driver for all tasks
#     output=None,
#     block_images_and_css=True,
#     wait_for_complete_page_load=False,
# )
# def login_cbonds(driver: Driver, data=None):
#     """
#     Заходим на https://www.cbonds.ru, если есть кнопка "a.userInput" — логинимся.
#     Если её нет, просто выходим.
#     """
#     if not data:
#         data = {}
#     username = data.get("username", "Rzaev.G.Em@sberbank.ru")
#     password = data.get("password", "Kemal170718")
#     otp_code = data.get("otp_code", "7358")

#     driver.get("https://www.cbonds.ru/", wait=Wait.SHORT, bypass_cloudflare=True)

#     # 2) Проверяем, есть ли кнопка "a.userInput"
#     login_btn = driver.select("a.userInput", wait=Wait.SHORT)
#     if not login_btn:
#         # Значит, мы уже залогинены или сайт не требует логин.
#         return

#     # 3) Клик и вводим логин/пароль
#     driver.click("a.userInput", wait=Wait.SHORT)
#     driver.type("input[name='login']", username)
#     driver.type("input[name='password']", password)
#     driver.click("input[type='submit']", wait=Wait.SHORT)

#     # 4) Если сайт требует OTP
#     code_input = driver.select("input[name='auth_email_code']", wait=Wait.SHORT)
#     if code_input:
#         if otp_code:
#             driver.type("input[name='auth_email_code']", otp_code)
#             driver.click("input[type='submit']", wait=Wait.SHORT)
#         else:
#             # Либо driver.prompt(), либо прерываемся
#             driver.prompt("Введи код вручную и нажми Enter в консоли...")


@browser(
    cache=False,
    max_retry=5,  # Retry up to 5 times, which is a good default
    reuse_driver=True,  # Reuse the same driver for all tasks
    # output=None,
    close_on_crash=True,
    raise_exception=True,
    create_error_logs=False,
    block_images_and_css=True,
    wait_for_complete_page_load=False,
)
def fetch_news_list_as_json(driver: Driver, url):
    """
    Предполагаем, что мы уже залогинены (или логин не нужен).
    Просто переходим на URL, ждём список <ul.newsList li> и собираем данные.
    """
    otp = OTP.load()
    data = {}
    username = data.get("username", settings.CBONDS_USERNAME)
    password = data.get("password", settings.CBONDS_PASSWORD)
    otp_code = data.get("otp_code", otp.code if otp else settings.CBONDS_OTP)

    driver.google_get("https://www.cbonds.ru/", wait=Wait.SHORT, bypass_cloudflare=True)

    # 2) Проверяем, есть ли кнопка "a.userInput"
    login_btn = driver.select("a.userInput", wait=Wait.SHORT)
    if login_btn:
        # 3) Клик и вводим логин/пароль
        driver.click("a.userInput", wait=Wait.SHORT)
        driver.type("input[name='login']", username)
        driver.type("input[name='password']", password)
        driver.click("input[type='submit']", wait=Wait.SHORT)
        logger.info("Логинимся...")

    # 4) Если сайт требует OTP
    code_input = driver.select("input[name='auth_email_code']", wait=Wait.SHORT)
    if code_input:
        logger.info("Вводим OTP...")
        if otp_code:
            driver.type("input[name='auth_email_code']", otp_code)
            driver.click("input[type='submit']", wait=Wait.SHORT)
            # Делаем небольшую паузу, чтобы страница успела перезагрузиться
            time.sleep(2)

        # Пробуем найти то же самое поле снова
        still_code_input = driver.select(
            "input[name='auth_email_code']", wait=Wait.SHORT
        )

        if still_code_input:
            # Значит, поле ввода OTP так и не пропало => предполагаем, что код неверный.
            logger.error("OTP неверен, так как форма осталась.")
            notify_admins_invalid_otp(otp_code)
            raise InvalidOTPError("Неверный код OTP")

    driver.get(url, wait=Wait.SHORT, bypass_cloudflare=True)

    driver.select("ul.newsList li", wait=Wait.LONG)

    with open("news.html", "w", encoding="utf-8") as f:
        f.write(driver.page_html)

    li_elements = driver.select_all("ul.newsList li")
    results = []
    for li in li_elements:
        title_el = li.select(".info a.ttl")
        if not title_el:
            continue
        news_title = title_el.text.strip()
        news_link = title_el.get_attribute("href")
        time_el = li.select(".time")
        time_text = time_el.text.strip() if time_el else ""
        news_id = extract_news_id(news_link)
        results.append(
            {
                "title": news_title,
                "url": news_link,
                "id": news_id,
                "time": time_text,
            }
        )
    return results
