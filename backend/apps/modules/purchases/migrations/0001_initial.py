from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ruc', models.CharField(blank=True, max_length=13, verbose_name='RUC/Cédula')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
                'db_table': 'purchases_supplier',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('status', models.CharField(
                    choices=[('pending', 'Pendiente'), ('received', 'Recibida'), ('cancelled', 'Cancelada')],
                    default='pending', max_length=20,
                )),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('supplier', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='purchases', to='purchases.supplier',
                )),
            ],
            options={
                'verbose_name': 'Compra',
                'verbose_name_plural': 'Compras',
                'db_table': 'purchases_purchase',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('purchase', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items', to='purchases.purchase',
                )),
            ],
            options={
                'verbose_name': 'Ítem de compra',
                'verbose_name_plural': 'Ítems de compra',
                'db_table': 'purchases_purchaseitem',
            },
        ),
    ]
