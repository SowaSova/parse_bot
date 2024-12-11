from django.contrib import admin

from .models import TelegramUser


@admin.register(TelegramUser)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "telegram_id",
        "tg_username",
        "created_at",
    ]
    search_fields = ["telegram_id"]
    list_filter = ["created_at"]
