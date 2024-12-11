from aiogram import Router
from aiogram.types import CallbackQuery

from tg_bot.domain import keyboards as kb
from tg_bot.domain.callbacks import PaginationCallback

router = Router()


@router.callback_query(PaginationCallback.filter())
async def paginate(
    callback_query: CallbackQuery, callback_data: PaginationCallback
):
    action = callback_data.action
    page = callback_data.page
    entity = callback_data.entity

    if entity == "category":
        keyboard = await kb.get_categories_keyboard(page=page)
    elif entity == "country":
        keyboard = await kb.get_countries_keyboard(page=page)
    else:
        await callback_query.answer("Неизвестный тип пагинации.")
        return

    if keyboard:
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback_query.answer("Нет доступных страниц.")
    await callback_query.answer()
