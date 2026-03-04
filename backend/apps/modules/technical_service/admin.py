from django.contrib import admin
from .models import ServiceTicket


@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'client_name', 'device', 'status', 'priority', 'received_at', 'final_cost']
    list_filter = ['status', 'priority']
    search_fields = ['client_name', 'device', 'serial_number', 'client_phone']
    readonly_fields = ['received_at', 'created_at', 'updated_at']
    list_editable = ['status', 'priority']
