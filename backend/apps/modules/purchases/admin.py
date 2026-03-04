from django.contrib import admin
from .models import Supplier, Purchase, PurchaseItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'ruc', 'email', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'ruc']


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'date', 'status', 'total']
    list_filter = ['status']
    search_fields = ['supplier__name']
    inlines = [PurchaseItemInline]
    readonly_fields = ['total', 'created_at', 'updated_at']
