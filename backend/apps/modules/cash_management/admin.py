from django.contrib import admin
from .models import CashMovement


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ['date', 'type', 'category', 'description', 'amount']
    list_filter = ['type', 'category']
    search_fields = ['description']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
