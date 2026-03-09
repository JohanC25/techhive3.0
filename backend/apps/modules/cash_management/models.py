from django.db import models


class CashMovement(models.Model):
    TYPE_CHOICES = [
        ('income', 'Ingreso'),
        ('expense', 'Egreso'),
    ]
    CATEGORY_CHOICES = [
        ('sale', 'Venta'),
        ('purchase', 'Compra'),
        ('salary', 'Salario'),
        ('service', 'Servicio técnico'),
        ('rent', 'Arriendo'),
        ('utility', 'Servicios básicos'),
        ('other', 'Otro'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Tipo')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name='Categoría')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto')
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cash_movement'
        verbose_name = 'Movimiento de caja'
        verbose_name_plural = 'Movimientos de caja'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"[{self.type}] {self.description} — ${self.amount}"
