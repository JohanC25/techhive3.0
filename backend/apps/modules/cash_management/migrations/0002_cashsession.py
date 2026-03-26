from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cash_management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CashSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Fecha')),
                ('opening_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto inicial')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Hora de cierre')),
                ('closing_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True,
                                                        verbose_name='Monto de cierre')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('opened_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Abierta por',
                )),
            ],
            options={
                'verbose_name': 'Sesión de caja',
                'verbose_name_plural': 'Sesiones de caja',
                'db_table': 'cash_session',
                'ordering': ['-date'],
            },
        ),
    ]
