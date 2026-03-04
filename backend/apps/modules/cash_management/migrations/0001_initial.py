from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CashMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(
                    choices=[('income', 'Ingreso'), ('expense', 'Egreso')],
                    max_length=10, verbose_name='Tipo',
                )),
                ('category', models.CharField(
                    choices=[
                        ('sale', 'Venta'), ('purchase', 'Compra'), ('salary', 'Salario'),
                        ('service', 'Servicio técnico'), ('rent', 'Arriendo'),
                        ('utility', 'Servicios básicos'), ('other', 'Otro'),
                    ],
                    default='other', max_length=20, verbose_name='Categoría',
                )),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto')),
                ('date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Movimiento de caja',
                'verbose_name_plural': 'Movimientos de caja',
                'db_table': 'cash_movement',
                'ordering': ['-date', '-created_at'],
            },
        ),
    ]
