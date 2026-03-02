from django.db import models


class Venta(models.Model):
    """
    Modelo principal de ventas.
    Incluye campos para análisis predictivo (feriado, fin de semana, método de pago).
    """

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('deuna', 'DeUna'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('otro', 'Otro'),
    ]

    # ── Campos principales ──────────────────────────────
    fecha_venta         = models.DateField()
    descripcion         = models.CharField(max_length=255)
    cantidad            = models.PositiveIntegerField(default=1)
    precio_unitario_pub = models.DecimalField(max_digits=10, decimal_places=2,
                                              verbose_name='Precio unitario público')
    precio_unitario_emp = models.DecimalField(max_digits=10, decimal_places=2,
                                              verbose_name='Precio unitario empresa',
                                              null=True, blank=True)
    total               = models.DecimalField(max_digits=10, decimal_places=2,
                                              verbose_name='Valor final')
    metodo_pago         = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES,
                                           default='efectivo')

    # ── Campos para modelo predictivo ───────────────────
    es_feriado          = models.BooleanField(default=False)
    es_fin_de_semana    = models.BooleanField(default=False)
    mes                 = models.PositiveSmallIntegerField(null=True, blank=True)
    dia_semana          = models.PositiveSmallIntegerField(null=True, blank=True,
                                                           help_text='0=Lunes, 6=Domingo')

    # ── Timestamps ──────────────────────────────────────
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ventas_venta'
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def save(self, *args, **kwargs):
        # Auto-calcular campos derivados de la fecha
        if self.fecha_venta:
            self.mes = self.fecha_venta.month
            self.dia_semana = self.fecha_venta.weekday()  # 0=Lunes, 6=Domingo
            self.es_fin_de_semana = self.dia_semana >= 5  # Sab=5, Dom=6
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha_venta} | {self.descripcion} | ${self.total}"