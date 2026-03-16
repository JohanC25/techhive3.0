from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
        ('inventory', '0002_shelf'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Eliminar campos que se mueven a VentaItem
        migrations.RemoveField(model_name='venta', name='descripcion'),
        migrations.RemoveField(model_name='venta', name='cantidad'),
        migrations.RemoveField(model_name='venta', name='precio_unitario_pub'),
        migrations.RemoveField(model_name='venta', name='precio_unitario_emp'),

        # Agregar FK de cliente
        migrations.AddField(
            model_name='venta',
            name='client',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ventas',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Cliente',
                limit_choices_to={'role': 'client'},
            ),
        ),

        # Dar valor por defecto 0 al total existente (ya era requerido antes)
        migrations.AlterField(
            model_name='venta',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total'),
        ),

        # Crear tabla VentaItem
        migrations.CreateModel(
            name='VentaItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255, verbose_name='Descripción')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Cantidad')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio unitario')),
                ('subtotal', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('venta', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='sales.venta',
                )),
                ('product', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='venta_items',
                    to='inventory.product',
                    verbose_name='Producto',
                )),
            ],
            options={
                'verbose_name': 'Ítem de venta',
                'verbose_name_plural': 'Ítems de venta',
                'db_table': 'ventas_ventaitem',
            },
        ),
    ]
