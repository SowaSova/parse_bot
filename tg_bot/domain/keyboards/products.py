from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from apps.products.models import Product
from tg_bot.domain.callbacks import ProductCallback
from tg_bot.domain.services.products import get_products

from .control import get_back_button_or_builder


async def get_products_keyboard(products: list[Product] = None):
    kb = InlineKeyboardBuilder()
    for product in products:
        kb.row(
            InlineKeyboardButton(
                text=product.title, callback_data=ProductCallback(id=product.id).pack()
            )
        )
    kb.attach(get_back_button_or_builder(entity="main", builder=True))
    return kb.as_markup()


async def get_product_keyboard(product_id: int):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="Купить",
            callback_data=ProductCallback(id=product_id, action="buy").pack(),
        )
    )
    kb.attach(get_back_button_or_builder(entity="products", builder=True))
    return kb.as_markup()
