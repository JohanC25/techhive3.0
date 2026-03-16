from django.db.models import F
from rest_framework import serializers
from .models import Venta, VentaItem


class VentaItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = VentaItem
        fields = ['id', 'product', 'product_name', 'description', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['subtotal']


class VentaSerializer(serializers.ModelSerializer):
    items = VentaItemSerializer(many=True, required=True)
    client_name = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'id', 'client', 'client_name', 'fecha_venta', 'total',
            'metodo_pago', 'es_feriado', 'es_fin_de_semana',
            'mes', 'dia_semana', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['total', 'mes', 'dia_semana', 'es_fin_de_semana', 'created_at', 'updated_at']

    def get_client_name(self, obj):
        if obj.client:
            return obj.client.get_full_name() or obj.client.username
        return None

    def _descontar_stock(self, product_id, quantity):
        from apps.modules.inventory.models import Product
        Product.objects.filter(pk=product_id, stock__gte=quantity).update(stock=F('stock') - quantity)

    def _restaurar_stock(self, product_id, quantity):
        from apps.modules.inventory.models import Product
        Product.objects.filter(pk=product_id).update(stock=F('stock') + quantity)

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        venta = Venta.objects.create(**validated_data)
        for item_data in items_data:
            item = VentaItem.objects.create(venta=venta, **item_data)
            if item.product_id:
                self._descontar_stock(item.product_id, item.quantity)
        venta.recalculate_total()
        # Registrar en caja aquí (después de recalculate_total) para usar el total correcto
        try:
            from apps.modules.cash_management.models import CashMovement
            CashMovement.objects.create(
                type='income',
                category='sale',
                description=f'Venta #{venta.id}',
                amount=venta.total,
                date=venta.fecha_venta,
            )
        except Exception:
            pass
        return venta

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            # Restaurar stock de ítems anteriores
            for old_item in instance.items.all():
                if old_item.product_id:
                    self._restaurar_stock(old_item.product_id, old_item.quantity)
            instance.items.all().delete()
            for item_data in items_data:
                item = VentaItem.objects.create(venta=instance, **item_data)
                if item.product_id:
                    self._descontar_stock(item.product_id, item.quantity)
            instance.recalculate_total()
            try:
                from apps.modules.cash_management.models import CashMovement
                CashMovement.objects.update_or_create(
                    category='sale',
                    description=f'Venta #{instance.id}',
                    defaults={
                        'type': 'income',
                        'amount': instance.total,
                        'date': instance.fecha_venta,
                    },
                )
            except Exception:
                pass
        return instance
