from django.db import models

from utils import get_username


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="ID Telegram", null=True, blank=True
    )
    tg_username = models.CharField(
        max_length=255, verbose_name="TG Username", null=True, blank=True
    )
    full_name = models.CharField(max_length=255, verbose_name="Полное имя", null=True)
    phone_number = models.CharField(
        max_length=20, verbose_name="Номер телефона", null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "TG-Пользователь"
        verbose_name_plural = "TG-Пользователи"

    def __str__(self):
        return self.tg_username or self.telegram_id or str(self.created_at)

    def save(self, *args, **kwargs):
        self.tg_username = get_username(self.tg_username)
        super().save(*args, **kwargs)
