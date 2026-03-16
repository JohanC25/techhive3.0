from django.contrib import admin
from .models import Venta, VentaItem


class VentaItemInline(admin.TabularInline):
    model = VentaItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['fecha_venta', 'client', 'total', 'metodo_pago']
    list_filter = ['metodo_pago', 'es_feriado', 'es_fin_de_semana', 'mes']
    search_fields = ['client__username', 'client__first_name']
    date_hierarchy = 'fecha_venta'
    readonly_fields = ['total', 'mes', 'dia_semana', 'es_fin_de_semana', 'created_at', 'updated_at']
    inlines = [VentaItemInline]
