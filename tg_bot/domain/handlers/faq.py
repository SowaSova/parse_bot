import logging

from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from tg_bot.domain import keyboards as kb
from tg_bot.domain.services import get_faq

logger = logging.getLogger(__name__)

router = Router()


@router.inline_query()
async def inline_faq_handler(inline_query: InlineQuery, bot: Bot):
    """
    Обработчик для обработки inline-запросов с FAQ.
    """
    try:
        query = inline_query.query.lower()
        results = []

        faqs = await get_faq(query)

        for faq in faqs:
            result = InlineQueryResultArticle(
                id=str(faq.id),
                title=faq.question,
                input_message_content=InputTextMessageContent(message_text=faq.answer),
            )
            results.append(result)

        if not results:
            results.append(
                InlineQueryResultArticle(
                    id="not_found",
                    title="Вопрос не найден",
                    input_message_content=InputTextMessageContent(
                        message_text="К сожалению, я не нашел ответ на ваш вопрос."
                    ),
                )
            )

        await bot.answer_inline_query(inline_query.id, results=results, cache_time=1)
        logger.info(
            f"User {inline_query.from_user.id} performed FAQ inline query: '{query}'"
        )
    except Exception as e:
        logger.error(f"Error in inline_faq_handler: {e}")
        await bot.answer_inline_query(inline_query.id, results=[], cache_time=1)


@router.callback_query(F.data == "faq_instructions")
async def show_faq(callback_query: types.CallbackQuery, bot: Bot):
    """
    Обработчик для отображения инструкций по использованию FAQ через inline-запросы.
    """
    try:
        bot_username = await bot.me()

        await callback_query.message.edit_text(
            "Для просмотра списка вопросов и ответов\n"
            "скопируйте имя бота в поле сообщения и введите ваш вопрос:\n\n"
            f"<code>@{bot_username.username}</code>",
            reply_markup=kb.get_faq_instruction_keyboard(),
        )
        await callback_query.answer()
        logger.info(f"User {callback_query.from_user.id} requested FAQ instructions.")
    except Exception as e:
        logger.error(f"Error in show_faq: {e}")
        await callback_query.message.reply("Произошла ошибка при отображении FAQ.")
        await callback_query.answer()
