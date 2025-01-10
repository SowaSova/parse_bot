import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from apps.users.models import TelegramUser
from tg_bot.domain import keyboards as kb
from tg_bot.domain.callbacks import ProductCallback
from tg_bot.domain.services import get_or_create_cart, get_product_by_id, get_products

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "products")
async def product_list_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    products = await get_products()
    if not products:
        await callback_query.answer("Нет доступных товаров.")
        return

    mkup = await kb.get_products_keyboard(products=products)
    await callback_query.message.edit_reply_markup(reply_markup=mkup)
    await callback_query.answer()


@router.callback_query(ProductCallback.filter(F.action != "buy"))
async def product_handler(
    callback_query: CallbackQuery, callback_data: ProductCallback, user: TelegramUser
):
    product = await get_product_by_id(callback_data.id)
    if not product:
        await callback_query.message.edit_text("Товар не найден.")
        return
    mkup = await kb.get_product_keyboard(callback_data.id)
    msg = f"<b>{product.title}</b>\n\n{product.description}"

    if product.image:
        photo = FSInputFile(product.image.path)
        await callback_query.message.delete()
        await callback_query.message.answer_photo(photo, caption=msg, reply_markup=mkup)
    else:
        await callback_query.message.edit_text(msg, reply_markup=mkup)
    await callback_query.answer()


@router.callback_query(ProductCallback.filter(F.action == "buy"))
async def buy_handler(
    callback_query: CallbackQuery, callback_data: ProductCallback, user: TelegramUser
):
    await callback_query.message.delete()
    mkup = await kb.get_main_keyboard()
    try:
        await get_or_create_cart(user, callback_data.id)
        await callback_query.message.answer(
            "Готово! В ближайшее время менеджер с вами свяжется.",
            reply_markup=mkup,
        )
    except Exception as e:
        logger.error("Ошибка в создании покупки: %s", e)
        await callback_query.message.answer(
            "Произошла ошибка, попробуйте ещё раз позже.",
            reply_markup=mkup,
        )
        await callback_query.answer()
