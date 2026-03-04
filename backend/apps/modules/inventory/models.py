from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_category'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products'
    )
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio de venta')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo')
    stock = models.PositiveIntegerField(default=0)
    stock_min = models.PositiveIntegerField(default=0, verbose_name='Stock mínimo')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventory_product'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def low_stock(self):
        return self.stock <= self.stock_min
