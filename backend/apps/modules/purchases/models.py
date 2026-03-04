from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    ruc = models.CharField(max_length=13, blank=True, verbose_name='RUC/Cédula')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'purchases_supplier'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['name']

    def __str__(self):
        return self.name


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('received', 'Recibida'),
        ('cancelled', 'Cancelada'),
    ]

    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, related_name='purchases'
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'purchases_purchase'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-date']

    def __str__(self):
        return f"Compra #{self.id} — {self.supplier} ({self.date})"

    def recalculate_total(self):
        from django.db.models import Sum
        result = self.items.aggregate(total=Sum('subtotal'))
        self.total = result['total'] or 0
        self.save(update_fields=['total'])


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, related_name='items'
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        db_table = 'purchases_purchaseitem'
        verbose_name = 'Ítem de compra'
        verbose_name_plural = 'Ítems de compra'

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x{self.quantity}"
