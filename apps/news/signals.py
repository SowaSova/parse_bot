from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NewsFilter


@receiver(post_save, sender=NewsFilter)
def cache_news_filter_url(sender, instance, **kwargs):
    # Сохраняем ссылку в Redis-кэш
    cache.set("news_filter_url", instance.url, None)
