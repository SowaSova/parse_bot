from django.contrib import admin

from .models import Cart, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["title"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["product"]
