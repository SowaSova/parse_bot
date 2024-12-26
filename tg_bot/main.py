import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from django.conf import settings

from tg_bot.core.logger import configure_logger
from tg_bot.domain.handlers import register_handlers
from tg_bot.middlewares.auth import AuthMiddleware


async def main() -> None:
    # configure_logger(True)
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.update.middleware(AuthMiddleware())

    register_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info("Запуск бота")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
