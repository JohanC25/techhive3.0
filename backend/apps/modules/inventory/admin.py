from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock', 'stock_min', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'sku']
    list_editable = ['stock', 'is_active']
