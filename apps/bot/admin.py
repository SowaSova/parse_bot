from django.contrib import admin

from .models import BotButton, BotMedia, BotMessage, BotMessageType


@admin.register(BotButton)
class BotButtonAdmin(admin.ModelAdmin):
    list_display = ["payload", "text", "button_type", "message"]
    ordering = ["message", "order"]


@admin.register(BotMedia)
class BotMediaAdmin(admin.ModelAdmin):
    pass


@admin.register(BotMessageType)
class BotMessageTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ["identifier", "text"]
