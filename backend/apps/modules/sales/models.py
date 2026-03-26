from django.conf import settings
from django.db import models


class Venta(models.Model):
    """
    Cabecera de venta. Los ítems se registran en VentaItem.
    Incluye campos para análisis predictivo (feriado, fin de semana, método de pago).
    """

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('deuna', 'DeUna'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('otro', 'Otro'),
    ]

    # ── Relaciones ──────────────────────────────────────
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ventas',
        verbose_name='Cliente',
        limit_choices_to={'role': 'client'},
    )

    # ── Campos principales ──────────────────────────────
    fecha_venta = models.DateField()
    total       = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total', default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')

    # ── Campos para modelo predictivo ───────────────────
    es_feriado       = models.BooleanField(default=False)
    es_fin_de_semana = models.BooleanField(default=False)
    mes              = models.PositiveSmallIntegerField(null=True, blank=True)
    dia_semana       = models.PositiveSmallIntegerField(null=True, blank=True,
                                                        help_text='0=Lunes, 6=Domingo')

    # ── Timestamps ──────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ventas_venta'
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def save(self, *args, **kwargs):
        if self.fecha_venta:
            self.mes = self.fecha_venta.month
            self.dia_semana = self.fecha_venta.weekday()
            self.es_fin_de_semana = self.dia_semana >= 5
        super().save(*args, **kwargs)

    def recalculate_total(self):
        from django.db.models import Sum
        result = self.items.aggregate(total=Sum('subtotal'))
        self.total = result['total'] or 0
        self.save(update_fields=['total'])

    def __str__(self):
        return f"{self.fecha_venta} | ${self.total}"


class VentaItem(models.Model):
    """Línea de ítem dentro de una venta."""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='venta_items',
        verbose_name='Producto',
    )
    description = models.CharField(max_length=255, verbose_name='Descripción')
    quantity    = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    unit_price  = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio unitario')
    subtotal    = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        db_table = 'ventas_ventaitem'
        verbose_name = 'Ítem de venta'
        verbose_name_plural = 'Ítems de venta'

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x{self.quantity} = ${self.subtotal}"
