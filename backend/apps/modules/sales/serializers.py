from rest_framework import serializers
from .models import Venta


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = [
            'id', 'fecha_venta', 'descripcion', 'cantidad',
            'precio_unitario_pub', 'precio_unitario_emp', 'total',
            'metodo_pago', 'es_feriado', 'es_fin_de_semana',
            'mes', 'dia_semana', 'created_at', 'updated_at',
        ]
        read_only_fields = ['mes', 'dia_semana', 'es_fin_de_semana', 'created_at', 'updated_at']
