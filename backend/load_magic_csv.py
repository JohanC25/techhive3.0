"""
1. Vacía magic_world (ventas + ventaitems)
2. Carga BD_Ventas_Magic.csv (May 2025 – Jan 15 2026)
3. Genera seed consistente Jan 16 2026 → ayer (23 Mar)
4. Inserta 12 ventas de hoy
"""
import csv, django, os, sys, random
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from decimal import Decimal, InvalidOperation
from datetime import datetime, date, timedelta, timezone
import calendar

CSV_PATH = 'BD_Ventas_Magic.csv'
TENANT   = 'magic_world'

with schema_context(TENANT):
    from apps.modules.sales.models import Venta, VentaItem
    from apps.modules.inventory.models import Product

    # ── 1. VACIAR ────────────────────────────────────────────────────────────
    print('Vaciando magic_world...')
    vi_del = VentaItem.objects.all().delete()
    v_del  = Venta.objects.all().delete()
    print(f'  Eliminados: {v_del[0]} ventas, {vi_del[0]} ventaitems')

    # ── 2. CARGAR CSV ─────────────────────────────────────────────────────────
    print(f'\nCargando {CSV_PATH}...')

    def parse_bool(val):
        return val.strip().lower() == 't'

    def parse_metodo(pagado_deuna):
        if pagado_deuna:
            return 'deuna'
        return random.choices(
            ['efectivo', 'efectivo', 'efectivo', 'transferencia', 'tarjeta'],
            weights=[60, 0, 0, 20, 20]  # 60% efectivo, 20% transferencia, 20% tarjeta
        )[0]

    def parse_metodo(pagado_deuna):
        if pagado_deuna:
            return 'deuna'
        return random.choices(
            ['efectivo', 'transferencia', 'tarjeta'],
            weights=[60, 20, 20]
        )[0]

    ventas_csv = []
    errores = 0
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                fecha_str = row['fecha_venta'].strip()   # M/D/YYYY
                dt = datetime.strptime(fecha_str, '%m/%d/%Y')
                dt = dt.replace(hour=random.randint(8, 19),
                                minute=random.randint(0, 59),
                                tzinfo=timezone.utc)
                monto = Decimal(str(row['monto_venta']).strip())
                desc  = row['descripcion'].strip()[:255]
                feriado  = parse_bool(row['es_feriado'])
                finde    = parse_bool(row['es_fin_de_semana'])
                deuna    = parse_bool(row['pagado_deuna'])
                metodo   = parse_metodo(deuna)
                ventas_csv.append((dt, monto, desc, feriado, finde, metodo))
            except (ValueError, InvalidOperation) as e:
                errores += 1

    print(f'  Filas leídas: {len(ventas_csv)}  |  Errores: {errores}')

    # Bulk insert para velocidad
    ventas_objs = []
    for dt, monto, desc, feriado, finde, metodo in ventas_csv:
        ventas_objs.append(Venta(
            fecha_venta=dt,
            total=monto,
            metodo_pago=metodo,
            es_feriado=feriado,
            es_fin_de_semana=finde,
        ))

    creadas = Venta.objects.bulk_create(ventas_objs)
    print(f'  Ventas creadas: {len(creadas)}')

    # VentaItems correspondientes (1 por venta)
    items_objs = []
    for v_obj, (dt, monto, desc, feriado, finde, metodo) in zip(creadas, ventas_csv):
        items_objs.append(VentaItem(
            venta=v_obj,
            product=None,
            description=desc,
            quantity=1,
            unit_price=monto,
            subtotal=monto,
        ))
    VentaItem.objects.bulk_create(items_objs)
    print(f'  VentaItems creados: {len(items_objs)}')

    # ── 3. SEED CONSISTENTE Jan 16 2026 → 23 Mar 2026 ───────────────────────
    # Calcular estadísticas del CSV para mantener consistencia
    total_csv   = sum(m for _, m, *_ in ventas_csv)
    dias_csv    = (date(2026, 1, 15) - date(2025, 5, 31)).days + 1  # 230 días
    daily_ventas = len(ventas_csv) / dias_csv          # ~11.8/día
    daily_total  = float(total_csv) / dias_csv         # $/día
    avg_monto    = float(total_csv) / len(ventas_csv)  # $/venta

    print(f'\nEstadísticas CSV:')
    print(f'  {len(ventas_csv)} ventas en {dias_csv} días')
    print(f'  ~{daily_ventas:.1f} ventas/día  |  ~${daily_total:.2f}/día  |  ${avg_monto:.2f}/venta promedio')

    # Descripciones reales del CSV para usar en el seed
    descripciones = list({desc for _, _, desc, *_ in ventas_csv if len(desc) > 2})

    productos = list(Product.objects.filter(is_active=True, price__gt=0))

    def venta_consistente(fecha_dt):
        """Crea una venta con monto cercano al promedio del CSV."""
        desc  = random.choice(descripciones)
        monto = Decimal(str(round(random.gauss(avg_monto, avg_monto * 0.4), 2)))
        monto = max(Decimal('0.50'), monto)

        # Si hay producto con nombre parecido, enlazarlo (opcional)
        prod = None
        if productos and random.random() > 0.6:
            prod = random.choice(productos)
            monto = prod.price * random.randint(1, 2)
            desc  = prod.name

        metodo = random.choices(
            ['efectivo', 'transferencia', 'tarjeta', 'deuna'],
            weights=[60, 15, 15, 10]
        )[0]
        finde   = fecha_dt.weekday() >= 5
        feriado = False

        v = Venta(
            fecha_venta=fecha_dt,
            total=monto,
            metodo_pago=metodo,
            es_feriado=feriado,
            es_fin_de_semana=finde,
        )
        return v, VentaItem(
            venta=None,  # se asigna después
            product=prod,
            description=desc,
            quantity=1,
            unit_price=monto,
            subtotal=monto,
        )

    start_date = date(2026, 1, 16)
    end_date   = date(2026, 3, 23)   # hasta ayer
    delta      = (end_date - start_date).days + 1

    print(f'\nGenerando seed {start_date} → {end_date} ({delta} días)...')

    seed_ventas = []
    seed_items  = []
    for i in range(delta):
        d = start_date + timedelta(days=i)
        n_day = max(1, int(random.gauss(daily_ventas, daily_ventas * 0.25)))
        for _ in range(n_day):
            hour   = random.randint(8, 19)
            minute = random.randint(0, 59)
            dt = datetime(d.year, d.month, d.day, hour, minute, tzinfo=timezone.utc)
            v_obj, item_obj = venta_consistente(dt)
            seed_ventas.append(v_obj)
            seed_items.append(item_obj)

    creadas_seed = Venta.objects.bulk_create(seed_ventas)
    for v_obj, item_obj in zip(creadas_seed, seed_items):
        item_obj.venta = v_obj
    VentaItem.objects.bulk_create(seed_items)
    print(f'  Ventas seed: {len(creadas_seed)}  |  Items: {len(seed_items)}')

    # ── 4. HOY (24 Mar 2026) ─────────────────────────────────────────────────
    print('\nInsertando ventas de hoy...')
    now = datetime.now(tz=timezone.utc)
    hoy_ventas = []
    hoy_items  = []
    for _ in range(12):
        v_obj, item_obj = venta_consistente(now.replace(
            hour=random.randint(8, 19), minute=random.randint(0, 59)
        ))
        hoy_ventas.append(v_obj)
        hoy_items.append(item_obj)

    creadas_hoy = Venta.objects.bulk_create(hoy_ventas)
    for v_obj, item_obj in zip(creadas_hoy, hoy_items):
        item_obj.venta = v_obj
    VentaItem.objects.bulk_create(hoy_items)
    total_hoy = sum(float(v.total) for v in creadas_hoy)
    print(f'  {len(creadas_hoy)} ventas — ${total_hoy:.2f}')

    # ── 5. RESUMEN FINAL ──────────────────────────────────────────────────────
    print('\n=== RESULTADO FINAL magic_world ===')
    from django.db import connection as conn
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DATE_TRUNC('month', fecha_venta) as mes,
                   COUNT(*) as ventas, SUM(total) as total
            FROM ventas_venta
            GROUP BY DATE_TRUNC('month', fecha_venta)
            ORDER BY mes DESC LIMIT 12
        """)
        print(f"{'Mes':<10} | {'Ventas':>6} | {'Total':>10}")
        print('-' * 34)
        for r in cur.fetchall():
            print(f"{str(r[0])[:7]:<10} | {r[1]:>6} | ${float(r[2] or 0):>9,.2f}")

    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*), SUM(total) FROM ventas_venta WHERE DATE(fecha_venta) = %s", [date.today()])
        r = cur.fetchone()
        print(f"\nHoy: {r[0]} ventas — ${float(r[1] or 0):.2f}")
