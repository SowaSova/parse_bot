from django.db import models


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(
        unique=True, verbose_name="ID Telegram", null=True, blank=True
    )
    tg_username = models.CharField(
        max_length=255, verbose_name="TG Username", null=True, blank=True
    )
    is_verified = models.BooleanField(default=False, verbose_name="Подтверждён")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )

    class Meta:
        verbose_name = "TG-Пользователь"
        verbose_name_plural = "TG-Пользователи"

    def __str__(self):
        return self.tg_username or self.telegram_id or str(self.created_at)

    def save(self, *args, **kwargs):
        tg_url = "https://t.me/"
        if self.tg_username and self.tg_username.startswith("@"):
            self.tg_username = self.tg_username[1:]  # удаляем @
        if self.tg_username and self.tg_username.startswith(tg_url):
            self.tg_username = self.tg_username[len(tg_url) :]
        super().save(*args, **kwargs)
