from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tg_bot.domain import keyboards as kb
from tg_bot.domain.services.products import get_products

router = Router()


@router.callback_query(
    F.data.in_(
        [
            "back_to_main",
            "back_to_products",
        ]
    )
)
async def back_handler(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_main":
        mkup = await kb.get_main_keyboard()
        await state.clear()
        await callback_query.message.edit_text(
            "Выберите необходимый вариант",
            reply_markup=mkup,
        )
    if callback_query.data == "back_to_products":
        products = await get_products()
        if not products:
            await callback_query.answer("Нет доступных товаров.")
            return
        await callback_query.message.delete()
        mkup = await kb.get_products_keyboard(products=products)
        await callback_query.message.answer(
            text="Выберите необходимый продукт", reply_markup=mkup
        )
    await callback_query.answer()
