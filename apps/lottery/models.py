from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Lottery(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название розыгрыша")
    description = models.TextField(
        verbose_name="Описание розыгрыша", null=True, blank=True
    )
    photo = models.ImageField(
        upload_to="lotteries/", verbose_name="Фото розыгрыша", null=True, blank=True
    )
    fin_date = models.DateTimeField(verbose_name="Время окончания розыгрыша")
    winner = models.ForeignKey(
        "users.TelegramUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Победитель",
    )
    participants = models.ManyToManyField(
        "users.TelegramUser",
        verbose_name="Участники розыгрыша",
        related_name="lotteries",
        blank=True,
    )
    is_finished = models.BooleanField(default=False, verbose_name="Завершено")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Розыгрыш"
        verbose_name_plural = "Розыгрыши"
        ordering = ["-fin_date"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.fin_date and self.fin_date <= timezone.now():
            raise ValidationError(
                {"fin_date": "Время окончания не может быть в прошлом."}
            )
