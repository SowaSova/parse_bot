import logging
import random
import time

import cloudscraper
from django.conf import settings
from seleniumbase import SB
from seleniumbase.common.exceptions import LinkTextNotFoundException

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


def _human_delay(minimum=1.0, maximum=2.0):
    """Небольшая случайная задержка для имитации «человекоподобных» действий."""
    time.sleep(random.uniform(minimum, maximum))


def fetch_news_list_as_json(url: str):
    """
    Версия на SeleniumBase (UC Mode + CDP Mode).
    1) Активируем UC+CDP.
    2) Заходим на https://www.cbonds.ru/, при необходимости логинимся.
    3) Вводим OTP (если нужно).
    4) Переходим на URL.
    5) Парсим <ul.newsList li>.
    6) Возвращаем список словарей с результатами.
    """

    # Подготовка данных
    otp_obj = OTP.load()
    username = settings.CBONDS_USERNAME
    password = settings.CBONDS_PASSWORD
    otp_code = otp_obj.code if otp_obj else settings.CBONDS_OTP

    results = []

    # SeleniumBase позволяет запустить UC (undetected-chromedriver) + CDP
    # При желании можно передать больше аргументов (locale_code, proxy и т.д.)
    # "headless=True" (для headless-режима), "incognito=True", и пр.
    with SB(
        uc=True,
        uc_cdp=True,
        headless=True,
        incognito=True,
        browser="chrome",  # По умолчанию Chrome, но укажем явно
        timeout_multiplier=1.0,  # Можно увеличить, если сайт медленный
    ) as sb:
        try:
            # 1) Активация CDP Mode на главной странице сайта
            #    Это ОТКЛЮЧАЕТ WebDriver и переводит нас в "CDP-режим".
            sb.activate_cdp_mode("https://www.cbonds.ru/")
            logger.info("Открыли главную страницу cbonds (CDP Mode).")

            # 2) Ждем, пока Cloudflare пропустит (если это JS challenge)
            #    или просто даем сайту загрузиться
            sb.sleep(20)
            logger.info("Главная страница загружена.")

            # 3) Проверяем, есть ли кнопка логина (a.userInput)
            try:
                login_btn = sb.cdp.find_element("a.userInput")
                if login_btn:
                    logger.info("Кнопка логина найдена. Пытаемся логиниться...")
                    sb.cdp.click("a.userInput")
                    _human_delay()
                    sb.cdp.save_screenshot("output/login.png")
                    login_input = sb.cdp.find_element("input[name='login']")
                    pass_input = sb.cdp.find_element("input[name='password']")

                    # Можно использовать sb.cdp.type(...), чтобы эмулировать
                    # ввод через DevTools. Или sb.cdp.send_keys(...).
                    sb.cdp.type("input[name='login']", username)
                    _human_delay()
                    sb.cdp.type("input[name='password']", password)
                    _human_delay()

                    submit_btn = sb.cdp.find_element("input[type='submit']")
                    sb.cdp.click("input[type='submit']")
                    logger.info("Нажали Submit для логина.")
                    _human_delay(2, 3)
                else:
                    logger.info("Кнопка логина не найдена, возможно, уже залогинены.")
            except LinkTextNotFoundException:
                logger.info("Кнопка логина не найдена. Возможно, уже залогинены.")

            # 4) Проверяем, не требуется ли сайт ввести OTP
            try:
                code_input = sb.cdp.find_element(
                    "input[name='auth_email_code']", timeout=10
                )
                logger.info("Поле для OTP найдено.")
                if code_input:
                    logger.info("Сайт требует ввод OTP.")
                    if otp_code:
                        sb.cdp.type("input[name='auth_email_code']", otp_code)
                        _human_delay()
                        sb.cdp.click("input[type='submit']")
                        _human_delay(2, 3)

                        # Если поле все еще существует — OTP неверен
                        try:
                            sb.cdp.find_element("input[name='auth_email_code']")
                            # Не упали в except => поле на месте
                            logger.error("OTP неверен, так как форма осталась.")
                            notify_admins_invalid_otp(otp_code)
                            raise InvalidOTPError("Неверный код OTP")
                        except LinkTextNotFoundException:
                            logger.info("OTP принят, двигаемся дальше.")
                    else:
                        logger.warning("OTP код не задан. Прерываемся.")
                        raise InvalidOTPError("Отсутствует OTP-код.")
            except InvalidOTPError as e:
                logger.error(e)
                return []
            except Exception as e:
                logger.info(f"Поле для OTP не найдено. {e}")

            # 5) Открываем страницу с новостями
            sb.cdp.get(url)
            _human_delay()

            # Ждем появления ul.newsList li
            # но можем проверить, есть ли элемент
            # found_news = False
            # for _ in range(30):
            #     # 30 попыток (примерно ~30 секунд),
            #     # each iteration ~1s sleep
            #     sb.sleep(1)
            #     try:
            #         sb.cdp.find_element("ul.newsList li")
            #         found_news = True
            #         break
            #     except LinkTextNotFoundException:
            #         pass
            # if not found_news:
            #     logger.error("Не дождались списка новостей (ul.newsList li).")
            #     return []

            # 6) Сохраняем HTML
            # page_source = sb.cdp.get_page_source()
            sb.cdp.save_screenshot("output/news_page.png")
            # 7) Ищем все элементы li
            li_elements = sb.cdp.find_elements("ul.newsList li", timeout=20)
            for li_el in li_elements:
                # Ищем заголовок
                try:
                    title_el = li_el.query_selector(".info a.ttl")
                except LinkTextNotFoundException:
                    continue

                news_title = title_el.text.strip()
                news_link = title_el.get_attribute("href")

                # Ищем время
                try:
                    time_el = li_el.query_selector(".time")
                    time_text = time_el.text.strip()
                except LinkTextNotFoundException:
                    time_text = ""

                news_id = extract_news_id(news_link)

                results.append(
                    {
                        "title": news_title,
                        "url": news_link,
                        "id": news_id,
                        "time": time_text,
                    }
                )

        except InvalidOTPError:
            raise  # прокидываем дальше, чтобы Celery смог отловить
        except Exception as e:
            logger.exception(f"Ошибка при парсинге: {e}")
            return []
        # Конец блока `with SB(...) as sb:`

    return results


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


# @browser(
#     cache=False,
#     max_retry=5,  # Retry up to 5 times, which is a good default
#     reuse_driver=True,  # Reuse the same driver for all tasks
#     # output=None,
#     close_on_crash=True,
#     raise_exception=True,
#     create_error_logs=False,
#     block_images_and_css=True,
#     wait_for_complete_page_load=False,
# )
# def fetch_news_list_as_json(driver: Driver, url):
#     """
#     Предполагаем, что мы уже залогинены (или логин не нужен).
#     Просто переходим на URL, ждём список <ul.newsList li> и собираем данные.
#     """
#     otp = OTP.load()
#     data = {}
#     username = data.get("username", settings.CBONDS_USERNAME)
#     password = data.get("password", settings.CBONDS_PASSWORD)
#     otp_code = data.get("otp_code", otp.code if otp else settings.CBONDS_OTP)

#     driver.google_get("https://www.cbonds.ru/", wait=Wait.SHORT, bypass_cloudflare=True)

#     # 2) Проверяем, есть ли кнопка "a.userInput"
#     login_btn = driver.select("a.userInput", wait=Wait.SHORT)
#     if login_btn:
#         # 3) Клик и вводим логин/пароль
#         driver.click("a.userInput", wait=Wait.SHORT)
#         driver.type("input[name='login']", username)
#         driver.type("input[name='password']", password)
#         driver.click("input[type='submit']", wait=Wait.SHORT)
#         logger.info("Логинимся...")

#     # 4) Если сайт требует OTP
#     code_input = driver.select("input[name='auth_email_code']", wait=Wait.SHORT)
#     if code_input:
#         logger.info("Вводим OTP...")
#         if otp_code:
#             driver.type("input[name='auth_email_code']", otp_code)
#             driver.click("input[type='submit']", wait=Wait.SHORT)
#             # Делаем небольшую паузу, чтобы страница успела перезагрузиться
#             time.sleep(2)

#             # Пробуем найти то же самое поле снова
#             still_code_input = driver.select(
#                 "input[name='auth_email_code']", wait=Wait.SHORT
#             )

#             if still_code_input:
#                 # Значит, поле ввода OTP так и не пропало => предполагаем, что код неверный.
#                 logger.error("OTP неверен, так как форма осталась.")
#                 notify_admins_invalid_otp(otp_code)
#                 raise InvalidOTPError("Неверный код OTP")
#         else:
#             # Либо driver.prompt(), либо прерываемся
#             driver.prompt("Введи код вручную и нажми Enter в консоли...")

#     driver.get(url, wait=Wait.SHORT, bypass_cloudflare=True)

#     driver.select("ul.newsList li", wait=Wait.LONG)

#     with open("news.html", "w", encoding="utf-8") as f:
#         f.write(driver.page_html)

#     li_elements = driver.select_all("ul.newsList li")
#     results = []
#     for li in li_elements:
#         title_el = li.select(".info a.ttl")
#         if not title_el:
#             continue
#         news_title = title_el.text.strip()
#         news_link = title_el.get_attribute("href")
#         time_el = li.select(".time")
#         time_text = time_el.text.strip() if time_el else ""
#         news_id = extract_news_id(news_link)
#         results.append(
#             {
#                 "title": news_title,
#                 "url": news_link,
#                 "id": news_id,
#                 "time": time_text,
#             }
#         )
#     return results
