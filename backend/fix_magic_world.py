"""
Limpia Feb/Mar 2026 de magic_world y regenera datos consistentes para esos 2 meses.
Objetivo: mantener el mismo volumen/total promedio del resto de meses (referencia: 2025).
"""
import django, os, sys, random
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from decimal import Decimal
from datetime import datetime, date, timedelta, timezone
import calendar

TENANT = 'magic_world'

with schema_context(TENANT):
    from django.db import connection
    from apps.modules.sales.models import Venta, VentaItem
    from apps.modules.inventory.models import Product

    # 1. Ver estado actual
    print("=== ESTADO ACTUAL magic_world ===")
    with connection.cursor() as cur:
        cur.execute("""
            SELECT DATE_TRUNC('month', fecha_venta) as mes,
                   COUNT(*) as ventas, SUM(total) as total
            FROM ventas_venta
            GROUP BY DATE_TRUNC('month', fecha_venta)
            ORDER BY mes DESC LIMIT 6
        """)
        for r in cur.fetchall():
            print(f"  {str(r[0])[:7]}  |  {r[1]:4d} ventas  |  ${float(r[2] or 0):,.2f}")

    # 2. Calcular promedio mensual de 2025 (excluyendo meses problemáticos)
    with connection.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) as ventas, SUM(total) as total
            FROM ventas_venta
            WHERE fecha_venta >= '2025-04-01' AND fecha_venta < '2026-01-01'
        """)
        r = cur.fetchone()
        meses_ref = 9  # Apr-Dec 2025
        avg_ventas = int(r[0] / meses_ref)
        avg_total = float(r[1] or 0) / meses_ref
        avg_por_venta = float(r[1] or 0) / r[0] if r[0] else 25
    print(f"\nReferencia 2025 (Apr-Dec): {avg_ventas} ventas/mes, ${avg_total:,.2f}/mes, ${avg_por_venta:.2f}/venta promedio")

    # 3. Eliminar Feb y Mar 2026
    print("\nEliminando Feb y Mar 2026...")
    feb_ventas = Venta.objects.filter(fecha_venta__year=2026, fecha_venta__month=2)
    mar_ventas = Venta.objects.filter(fecha_venta__year=2026, fecha_venta__month=3)

    # Primero eliminar VentaItems
    VentaItem.objects.filter(venta__in=feb_ventas).delete()
    VentaItem.objects.filter(venta__in=mar_ventas).delete()

    feb_count = feb_ventas.count()
    mar_count = mar_ventas.count()
    feb_ventas.delete()
    mar_ventas.delete()
    print(f"  Eliminadas: {feb_count} ventas de Feb, {mar_count} ventas de Mar")

    # 4. Obtener productos activos
    productos = list(Product.objects.filter(is_active=True, price__gt=0))
    if not productos:
        print("ERROR: no hay productos")
        sys.exit(1)
    metodos = ['efectivo', 'tarjeta', 'transferencia']

    def random_date_in_month(year, month):
        days_in_month = calendar.monthrange(year, month)[1]
        day = random.randint(1, days_in_month)
        hour = random.randint(8, 19)
        minute = random.randint(0, 59)
        return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)

    def crear_venta_con_items(fecha):
        # Generar entre 1 y 4 items por venta
        n_items = random.choices([1, 2, 3, 4], weights=[40, 35, 15, 10])[0]
        total = Decimal('0')
        items_data = []
        for _ in range(n_items):
            prod = random.choice(productos)
            qty = random.randint(1, 3)
            sub = prod.price * qty
            total += sub
            items_data.append((prod, qty, sub))

        v = Venta.objects.create(
            fecha_venta=fecha,
            metodo_pago=random.choice(metodos),
            total=total
        )
        for prod, qty, sub in items_data:
            VentaItem.objects.create(
                venta=v, product=prod,
                description=prod.name,
                quantity=qty,
                unit_price=prod.price,
                subtotal=sub
            )
        return total

    # 5. Generar data para Feb y Mar 2026 con volumen consistente
    # Usar avg_ventas ± 10% para variación natural
    for year, month, label in [(2026, 2, 'Febrero 2026'), (2026, 3, 'Marzo 2026')]:
        n = int(avg_ventas * random.uniform(0.90, 1.10))
        # Para marzo: solo hasta el día 23 (hoy es 24 Mar, dejar hoy vacío para insertar real)
        if month == 3:
            days_available = 23  # hasta ayer
            days_in_month = calendar.monthrange(year, month)[1]
            n = int(n * days_available / days_in_month)

        total_mes = Decimal('0')
        for _ in range(n):
            fecha = random_date_in_month(year, month)
            # Para marzo: no pasar del día 23
            if month == 3:
                fecha = fecha.replace(day=min(fecha.day, 23))
            total_mes += crear_venta_con_items(fecha)

        print(f"  {label}: {n} ventas generadas, ${float(total_mes):,.2f}")

    # 6. Insertar ventas de HOY en marzo (12 ventas realistas para la demo)
    print("\nInsertando ventas de hoy (24 Mar)...")
    now = datetime.now(tz=timezone.utc)
    total_hoy = Decimal('0')
    for _ in range(12):
        total_hoy += crear_venta_con_items(now)
    print(f"  Hoy: 12 ventas, ${float(total_hoy):,.2f}")

    # 7. Estado final
    print("\n=== ESTADO FINAL magic_world ===")
    with connection.cursor() as cur:
        cur.execute("""
            SELECT DATE_TRUNC('month', fecha_venta) as mes,
                   COUNT(*) as ventas, SUM(total) as total
            FROM ventas_venta
            GROUP BY DATE_TRUNC('month', fecha_venta)
            ORDER BY mes DESC LIMIT 6
        """)
        for r in cur.fetchall():
            print(f"  {str(r[0])[:7]}  |  {r[1]:4d} ventas  |  ${float(r[2] or 0):,.2f}")

    with connection.cursor() as cur:
        cur.execute("SELECT COUNT(*), SUM(total) FROM ventas_venta WHERE DATE(fecha_venta) = %s", [date.today()])
        r = cur.fetchone()
        print(f"\nHoy: {r[0]} ventas — ${float(r[1] or 0):,.2f}")
