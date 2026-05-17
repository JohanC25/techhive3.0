"""
python manage.py setup_public_tenant
Crea el tenant público y registra admin.localhost como su dominio.
Debe correrse UNA vez después de la primera migración.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea el tenant público y registra admin.techhive-ec.com"

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
            domain='admin.techhive-ec.com',
            defaults={'tenant': pub, 'is_primary': True},
        )
        if created:
            self.stdout.write("  [+] Dominio admin.techhive-ec.com creado")
        else:
            self.stdout.write("  [=] Dominio admin.techhive-ec.com ya existía")

        self.stdout.write(self.style.SUCCESS("\nListo. Ahora admin.v.com sirve el portal admin."))
