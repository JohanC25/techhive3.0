from django.db import models


class ServiceTicket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En proceso'),
        ('waiting_parts', 'Esperando repuestos'),
        ('completed', 'Completado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]

    # Cliente
    client_name = models.CharField(max_length=255, verbose_name='Cliente')
    client_phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    client_email = models.EmailField(blank=True, verbose_name='Email')

    # Equipo
    device = models.CharField(max_length=255, verbose_name='Equipo/Dispositivo')
    serial_number = models.CharField(max_length=100, blank=True, verbose_name='N° Serie')
    accessories = models.TextField(blank=True, verbose_name='Accesorios entregados')

    # Diagnóstico
    problem = models.TextField(verbose_name='Problema reportado')
    diagnosis = models.TextField(blank=True, verbose_name='Diagnóstico técnico')
    solution = models.TextField(blank=True, verbose_name='Solución aplicada')

    # Económico
    estimated_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo estimado'
    )
    final_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Costo final'
    )

    # Estado
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Fechas
    received_at = models.DateField(auto_now_add=True, verbose_name='Fecha de recepción')
    promised_at = models.DateField(null=True, blank=True, verbose_name='Fecha prometida')
    completed_at = models.DateField(null=True, blank=True, verbose_name='Fecha de entrega')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'technical_service_ticket'
        verbose_name = 'Ticket de servicio'
        verbose_name_plural = 'Tickets de servicio'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id} — {self.client_name} | {self.device}"
