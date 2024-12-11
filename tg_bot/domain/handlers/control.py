from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tg_bot.domain import keyboards as kb

router = Router()


@router.callback_query(
    F.data.in_(
        [
            "back_to_channels",
            "back_to_main",
            "back_to_support",
            "back_to_channels_main",
            "back_to_categories",
            "back_to_countries",
            "back_to_subs_range",
        ]
    )
)
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_categories":
        mkup = await kb.get_categories_keyboard()
        await callback_query.message.edit_text(
            "Выберите категорию", reply_markup=mkup
        )
    if callback_query.data == "back_to_countries":
        mkup = await kb.get_countries_keyboard()
        await callback_query.message.edit_text(
            "Выберите страну", reply_markup=mkup
        )
    if callback_query.data == "back_to_subs_range":
        await callback_query.message.edit_text(
            "Выберите диапазон подписчиков",
            reply_markup=kb.get_subs_filter_keyboard(),
        )
    if callback_query.data == "back_to_channels":
        data = await state.get_data()
        if not data:
            return
        category = data.get("category")
        country = data.get("country")
        min_sub = data.get("min_subs")
        max_sub = data.get("max_subs")
        mkup = await kb.get_filtered_channels_keyboard(
            category=category,
            country=country,
            min_subs=min_sub,
            max_subs=max_sub,
        )
        await callback_query.message.edit_text(
            "Выберите канал",
            reply_markup=mkup,
        )
    if callback_query.data == "back_to_channels_main":
        await state.clear()
        await callback_query.message.edit_text(
            "Выберите необходимый вариант",
            reply_markup=kb.get_channels_keyboard(),
        )
    if callback_query.data == "back_to_support":
        await state.clear()
        await callback_query.message.edit_text(
            "Выберите удобный способ связи",
            reply_markup=kb.get_support_keyboard(),
        )
    if callback_query.data == "back_to_main":
        await state.clear()
        await callback_query.message.edit_text(
            "Привет! Я бот для проверки ссылок",
            reply_markup=kb.get_start_keyboard(),
        )
