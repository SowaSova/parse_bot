from django.core.exceptions import ValidationError
from django.db import models

from .utils import product_image_path


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название продукта")
    description = models.TextField(
        verbose_name="Описание продукта",
        null=True,
        blank=True,
    )
    image = models.ImageField(
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

    def clean(self):
        super().clean()
        desc_len = len(self.description or "")
        if self.image:
            # Если фото есть, ограничение 1024 символа
            if desc_len > 860:
                raise ValidationError(
                    {
                        "description": "Описание продукта + название продукта не может превышать 860 символа, если присутствует фото."
                    }
                )
        else:
            # Если фото нет, ограничение 4096 символов
            if desc_len > 3860:
                raise ValidationError(
                    {
                        "description": "Описание продукта не может превышать 3860 символов, если нет фото."
                    }
                )


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
