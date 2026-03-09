"""
Comando para cargar datos históricos de ventas desde CSV.
Uso:
    python manage.py cargar_ventas --tenant magic --archivo ruta/al/archivo.csv
    python manage.py cargar_ventas --tenant papeleria --archivo ruta/al/archivo.csv
"""

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context


FERIADOS_ECUADOR = [
    '01-01',  # Año Nuevo
    '02-28',  # Carnaval (aprox)
    '03-01',  # Carnaval (aprox)
    '04-18',  # Viernes Santo (aprox)
    '05-01',  # Día del Trabajo
    '05-24',  # Batalla de Pichincha
    '08-10',  # Primer Grito de Independencia
    '10-09',  # Independencia de Guayaquil
    '11-02',  # Día de Difuntos
    '11-03',  # Independencia de Cuenca
    '12-25',  # Navidad
]


def es_feriado(fecha: datetime.date) -> bool:
    mes_dia = fecha.strftime('%m-%d')
    return mes_dia in FERIADOS_ECUADOR


def parsear_fecha(texto: str) -> datetime.date | None:
    """Intenta parsear fecha en múltiples formatos."""
    formatos = ['%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    for fmt in formatos:
        try:
            return datetime.strptime(texto.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parsear_decimal(texto: str) -> Decimal:
    """Convierte texto a Decimal de forma segura."""
    try:
        limpio = texto.strip().replace(',', '').replace('$', '')
        return Decimal(limpio) if limpio else Decimal('0')
    except InvalidOperation:
        return Decimal('0')


class Command(BaseCommand):
    help = 'Carga ventas desde un CSV al schema del tenant indicado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            required=True,
            help='Schema del tenant (ej: magic, papeleria)'
        )
        parser.add_argument(
            '--archivo',
            type=str,
            required=True,
            help='Ruta al archivo CSV'
        )
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina ventas existentes antes de cargar'
        )

    def handle(self, *args, **options):
        tenant_schema = options['tenant']
        archivo = options['archivo']
        limpiar = options['limpiar']

        self.stdout.write(f"\n📂 Cargando: {archivo}")
        self.stdout.write(f"🏢 Tenant:   {tenant_schema}\n")

        with schema_context(tenant_schema):
            from apps.modules.sales.models import Venta

            if limpiar:
                cantidad = Venta.objects.count()
                Venta.objects.all().delete()
                self.stdout.write(f"🗑️  Eliminados {cantidad} registros existentes")

            creados = 0
            errores = 0

            with open(archivo, encoding='utf-8-sig', newline='') as f:
                reader = csv.DictReader(f)
                columnas = reader.fieldnames
                self.stdout.write(f"📋 Columnas detectadas: {columnas}\n")

                for i, row in enumerate(reader, start=1):
                    try:
                        # ── Fecha ──────────────────────────────────
                        fecha = parsear_fecha(row.get('fecha_venta', ''))
                        if not fecha:
                            self.stdout.write(f"  ⚠️  Fila {i}: fecha inválida → {row}")
                            errores += 1
                            continue

                        # ── Descripción ────────────────────────────
                        descripcion = row.get('descripcion', '').strip() or 'Sin descripción'

                        # ── Montos ─────────────────────────────────
                        # CSV Papelería tiene: cantidad_vendida, precio_unitario, total
                        # CSV Magic tiene: monto_venta (es el total directo)
                        if 'total' in row:
                            total = parsear_decimal(row['total'])
                        elif 'monto_venta' in row:
                            total = parsear_decimal(row['monto_venta'])
                        else:
                            total = Decimal('0')

                        if 'precio_unitario' in row:
                            precio_pub = parsear_decimal(row['precio_unitario'])
                        elif 'monto_venta' in row:
                            precio_pub = parsear_decimal(row['monto_venta'])
                        else:
                            precio_pub = total

                        if 'cantidad_vendida' in row:
                            cantidad = int(row['cantidad_vendida']) if row['cantidad_vendida'].strip() else 1
                        else:
                            cantidad = 1

                        # ── Método de pago ─────────────────────────
                        metodo = 'efectivo'
                        if 'pagado_deuna' in row:
                            val = row['pagado_deuna'].strip().lower()
                            if val in ('t', 'true', '1', 'si', 'sí'):
                                metodo = 'deuna'

                        # ── Crear venta ────────────────────────────
                        Venta.objects.create(
                            fecha_venta=fecha,
                            descripcion=descripcion,
                            cantidad=cantidad,
                            precio_unitario_pub=precio_pub,
                            total=total,
                            metodo_pago=metodo,
                            es_feriado=es_feriado(fecha),
                            # es_fin_de_semana y mes/dia_semana se calculan en save()
                        )
                        creados += 1

                        if creados % 500 == 0:
                            self.stdout.write(f"  ✅ {creados} registros cargados...")

                    except Exception as e:
                        self.stdout.write(f"  ❌ Fila {i} error: {e} → {row}")
                        errores += 1

            self.stdout.write(f"\n{'='*40}")
            self.stdout.write(f"✅ Cargados:  {creados}")
            self.stdout.write(f"❌ Errores:   {errores}")
            self.stdout.write(f"{'='*40}\n")