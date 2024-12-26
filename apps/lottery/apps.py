from django.apps import AppConfig


class LotteryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.lottery"
    verbose_name = "Розыгрыш"
    verbose_name_plural = "Розыгрыши"

    def ready(self):
        import apps.lottery.signals
