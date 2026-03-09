from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ServiceTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255, verbose_name='Cliente')),
                ('client_phone', models.CharField(blank=True, max_length=20, verbose_name='Teléfono')),
                ('client_email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('device', models.CharField(max_length=255, verbose_name='Equipo/Dispositivo')),
                ('serial_number', models.CharField(blank=True, max_length=100, verbose_name='N° Serie')),
                ('accessories', models.TextField(blank=True, verbose_name='Accesorios entregados')),
                ('problem', models.TextField(verbose_name='Problema reportado')),
                ('diagnosis', models.TextField(blank=True, verbose_name='Diagnóstico técnico')),
                ('solution', models.TextField(blank=True, verbose_name='Solución aplicada')),
                ('estimated_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Costo estimado')),
                ('final_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Costo final')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pendiente'), ('in_progress', 'En proceso'),
                        ('waiting_parts', 'Esperando repuestos'), ('completed', 'Completado'),
                        ('delivered', 'Entregado'), ('cancelled', 'Cancelado'),
                    ],
                    default='pending', max_length=20,
                )),
                ('priority', models.CharField(
                    choices=[
                        ('low', 'Baja'), ('medium', 'Media'),
                        ('high', 'Alta'), ('urgent', 'Urgente'),
                    ],
                    default='medium', max_length=10,
                )),
                ('received_at', models.DateField(auto_now_add=True, verbose_name='Fecha de recepción')),
                ('promised_at', models.DateField(blank=True, null=True, verbose_name='Fecha prometida')),
                ('completed_at', models.DateField(blank=True, null=True, verbose_name='Fecha de entrega')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Ticket de servicio',
                'verbose_name_plural': 'Tickets de servicio',
                'db_table': 'technical_service_ticket',
                'ordering': ['-created_at'],
            },
        ),
    ]
