from django.db import migrations


def seed_categories(apps, schema_editor):
    Category = apps.get_model('inventory', 'Category')
    for name in ['Servicio', 'Producto', 'Reparación']:
        Category.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_shelf'),
    ]

    operations = [
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
