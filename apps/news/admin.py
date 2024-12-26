from django.contrib import admin

from .models import Country, NewsChannel, NewsFilter


@admin.register(NewsChannel)
class NewsChannelAdmin(admin.ModelAdmin):
    list_display = ["id", "tg_username", "tg_id", "link"]
    list_editable = ["tg_username", "tg_id", "link"]

    def has_add_permission(self, request):
        if NewsChannel.objects.count() > 0:
            return False
        return super().has_add_permission(request)


@admin.register(NewsFilter)
class NewsFilterAdmin(admin.ModelAdmin):
    list_display = ["id", "url", "created_at"]
    list_editable = ["url"]

    def has_add_permission(self, request):
        if NewsFilter.objects.count() > 0:
            return False
        return super().has_add_permission(request)
