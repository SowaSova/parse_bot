from django.contrib import admin

from .models import FAQ, Manager


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ["id", "telegram_id", "tg_username", "created_at"]
    list_editable = ["telegram_id", "tg_username"]

    def has_add_permission(self, request):
        if Manager.objects.count() > 0:
            return False
        return super().has_add_permission(request)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ["question", "answer"]


# @admin.register(BotButton)
# class BotButtonAdmin(admin.ModelAdmin):
#     list_display = ["payload", "text", "button_type", "message"]
#     ordering = ["message", "order"]


# @admin.register(BotMedia)
# class BotMediaAdmin(admin.ModelAdmin):
#     pass


# @admin.register(BotMessageType)
# class BotMessageTypeAdmin(admin.ModelAdmin):
#     list_display = ["name", "description"]


# @admin.register(BotMessage)
# class BotMessageAdmin(admin.ModelAdmin):
#     list_display = ["identifier", "text"]
