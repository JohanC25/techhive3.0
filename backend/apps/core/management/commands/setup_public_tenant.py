"""
python manage.py setup_public_tenant
Crea el tenant público y registra admin.localhost como su dominio.
Debe correrse UNA vez después de la primera migración.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea el tenant público y registra admin.localhost."

    def handle(self, *args, **options):
        from apps.tenants.models import Company, Domain

        pub, created = Company.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'TechHive Admin'},
        )
        if created:
            self.stdout.write("  [+] Tenant público creado")
        else:
            self.stdout.write("  [=] Tenant público ya existía")

        dom, created = Domain.objects.get_or_create(
            domain='admin.localhost',
            defaults={'tenant': pub, 'is_primary': True},
        )
        if created:
            self.stdout.write("  [+] Dominio admin.localhost creado")
        else:
            self.stdout.write("  [=] Dominio admin.localhost ya existía")

        self.stdout.write(self.style.SUCCESS("\nListo. Ahora admin.localhost sirve el portal admin."))
