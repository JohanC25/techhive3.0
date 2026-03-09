from django.contrib import admin
from .models import Venta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['fecha_venta', 'descripcion', 'cantidad', 'total', 'metodo_pago']
    list_filter = ['metodo_pago', 'es_feriado', 'es_fin_de_semana', 'mes']
    search_fields = ['descripcion']
    date_hierarchy = 'fecha_venta'
    readonly_fields = ['mes', 'dia_semana', 'es_fin_de_semana', 'created_at', 'updated_at']
