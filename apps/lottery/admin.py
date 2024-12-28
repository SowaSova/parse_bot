from django.contrib import admin

from .models import Lottery


@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ["title", "fin_date"]
    search_fields = ["title"]
    list_filter = ["fin_date", "is_finished"]

    def get_readonly_fields(self, request, obj=None):
        """
        Делаем fin_date доступным только для чтения,
        если объект уже существует (obj.pk не None).
        """
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:  # означает, что мы редактируем уже существующий объект
            return readonly_fields + ("fin_date",)
        return readonly_fields
