from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('technical_service', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceticket',
            name='client_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Nombre cliente'),
        ),
        migrations.AddField(
            model_name='serviceticket',
            name='client',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={'role': 'client'},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tickets',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Cliente',
            ),
        ),
    ]
