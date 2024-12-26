from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.news"
    verbose_name = "Новость"
    verbose_name_plural = "Новости"

    def ready(self):
        import apps.news.signals  # noqa
