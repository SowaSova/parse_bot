from django.contrib.postgres.fields import ArrayField
from django.db import models

from config.singleton import SingletonModel
from utils import get_username

from .validators import validate_tg_id


class NewsFilter(SingletonModel):
    region = models.ManyToManyField("news.Region", verbose_name="Регион")
    language = models.ManyToManyField("news.Language", verbose_name="Язык")
    country = models.ManyToManyField("news.Country", verbose_name="Страна")
    news_type = models.ManyToManyField("news.NewsType", verbose_name="Тип новости")
    news_theme = models.ManyToManyField("news.NewsTheme", verbose_name="Тема новости")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Фильтр новостей"
        verbose_name_plural = "Фильтры новостей"


class NewsChannel(SingletonModel):
    link = models.URLField(verbose_name="Ссылка на канал", null=True, blank=True)
    tg_username = models.CharField(
        max_length=255, verbose_name="TG Username", null=True, blank=True
    )
    tg_id = models.BigIntegerField(
        verbose_name="ID Telegram", validators=[validate_tg_id]
    )

    class Meta:
        verbose_name = "Канал новостей"
        verbose_name_plural = "Каналы новостей"

    def __str__(self):
        return f"{self.tg_username or self.tg_id}"

    def save(self, *args, **kwargs):
        self.tg_username = get_username(self.link)
        super().save(*args, **kwargs)


class MainFilter(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    param_value = models.IntegerField(verbose_name="Значение")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Region(MainFilter):
    pass


class Language(MainFilter):
    param_value = models.CharField(verbose_name="Значение")


class Country(MainFilter):
    pass


class NewsType(MainFilter):
    pass


class NewsTheme(MainFilter):
    pass
