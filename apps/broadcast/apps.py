from django.apps import AppConfig


class BroadcastConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.broadcast"
    verbose_name = "Рассылка"
    verbose_name_plural = "Рассылки"

    def ready(self):
        import apps.broadcast.signals  # noqa
