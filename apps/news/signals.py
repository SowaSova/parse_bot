from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from apps.news.helpers import cache_filter_m2m_fields
from apps.news.tasks import parse_news_task

from .models import OTP, NewsFilter


@receiver(post_save, sender=OTP)
def otp_updated(sender, instance, created, **kwargs):
    # Если не при создании, а при обновлении
    if not created:
        parse_news_task.delay()


@receiver(post_save, sender=NewsFilter)
def cache_news_filter_url(sender, instance, **kwargs):
    """
    При сохранении фильтра:
      - Если is_url=True, сохраняем url в Redis-кэш
      - Иначе — удаляем его из кэша
    """
    if instance.url:
        cache.set("news_filter_url", instance.url, None)
    else:
        cache.delete("news_filter_url")


# @receiver(m2m_changed, sender=NewsFilter.region.through)
# def region_m2m_changed(sender, instance, action, **kwargs):
#     if action in ("post_add", "post_remove", "post_clear"):
#         # Обновляем кэш для M2M
#         cache_filter_m2m_fields(instance)


# @receiver(m2m_changed, sender=NewsFilter.country.through)
# def country_m2m_changed(sender, instance, action, **kwargs):
#     if action in ("post_add", "post_remove", "post_clear"):
#         cache_filter_m2m_fields(instance)


# @receiver(m2m_changed, sender=NewsFilter.news_type.through)
# def news_type_m2m_changed(sender, instance, action, **kwargs):
#     if action in ("post_add", "post_remove", "post_clear"):
#         cache_filter_m2m_fields(instance)


# @receiver(m2m_changed, sender=NewsFilter.news_theme.through)
# def news_theme_m2m_changed(sender, instance, action, **kwargs):
#     if action in ("post_add", "post_remove", "post_clear"):
#         cache_filter_m2m_fields(instance)
