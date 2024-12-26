from asgiref.sync import sync_to_async

from apps.products.models import Cart, Product
from apps.users.models import TelegramUser


@sync_to_async
def get_products():
    return list(Product.objects.all())


@sync_to_async
def get_product_by_id(product_id: int):
    return Product.objects.get(id=product_id)


@sync_to_async
def get_or_create_cart(user: TelegramUser, product_id: int):
    return Cart.objects.get_or_create(user_id=user.id, product_id=product_id)
