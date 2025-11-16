from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "quantity")
    search_fields = ("sku", "name")
    ordering = ("name",)
