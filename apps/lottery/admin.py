from django.contrib import admin

from .models import Lottery


@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    list_display = ["title", "fin_date"]
    search_fields = ["title"]
    list_filter = ["fin_date", "is_finished"]
