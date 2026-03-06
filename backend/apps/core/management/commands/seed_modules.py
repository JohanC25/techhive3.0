"""
python manage.py seed_modules
Crea los módulos del sistema en el schema público si no existen.
"""
from django.core.management.base import BaseCommand
from apps.core.models import Module

MODULES = [
    ("sales",             "Ventas"),
    ("inventory",         "Inventario"),
    ("purchases",         "Compras"),
    ("cash_management",   "Caja"),
    ("technical_service", "Servicio Técnico"),
    ("reports",           "Reportes"),
    ("chatbot",           "ChatBot IA"),
]


class Command(BaseCommand):
    help = "Crea los módulos del sistema en el schema público."

    def handle(self, *args, **options):
        created = 0
        for code, name in MODULES:
            _, was_created = Module.objects.get_or_create(code=code, defaults={"name": name})
            if was_created:
                self.stdout.write(f"  [+] {name}")
                created += 1
            else:
                self.stdout.write(f"  [=] {name} (ya existe)")
        self.stdout.write(self.style.SUCCESS(f"\nListo: {created} módulo(s) creados."))
