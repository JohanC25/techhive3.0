from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shelf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nombre de percha')),
                ('location', models.CharField(blank=True, max_length=255, verbose_name='Ubicación')),
            ],
            options={
                'verbose_name': 'Percha',
                'verbose_name_plural': 'Perchas',
                'db_table': 'inventory_shelf',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='shelf',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='products', to='inventory.shelf',
                verbose_name='Percha',
            ),
        ),
    ]
