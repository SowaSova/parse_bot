from django.db import models

from .utils import product_image_path


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название продукта")
    description = models.TextField(
        verbose_name="Описание продукта", null=True, blank=True
    )
    photo = models.ImageField(
        upload_to=product_image_path,
        verbose_name="Фото продукта",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.title


class Cart(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="Продукт"
    )
    user = models.ForeignKey(
        "users.TelegramUser", on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
