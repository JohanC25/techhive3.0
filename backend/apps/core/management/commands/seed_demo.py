"""
Management command para sembrar datos demo realistas en un tenant TechHive.

Negocio modelado: técnica informática + papelería + recargas (Quito, Ecuador)

Qué genera:
  • 3 perchas (Vitrina, Servicio Técnico, Bodega)
  • 6 categorías + ~32 productos con precios reales
  • N ventas recientes con VentaItem (últimos 60 días por defecto)
  • CashSession para hoy con $50 de apertura
  • CashMovements de egresos operativos del mes

Uso:
    python manage.py seed_demo --schema magic_world
    python manage.py seed_demo --schema papeleria --ventas 200 --dias 90
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand


# ─────────────────────────────────────────────
# CATÁLOGO DEL NEGOCIO
# (nombre, precio_venta, costo, categoria, stock_inicial, sku)
# ─────────────────────────────────────────────

CATALOGO = [
    # ── Servicios técnicos ──────────────────────────────────────────────
    ("Diagnóstico técnico",               Decimal("10.00"), Decimal("0.00"),  "Servicio",         999, "SVC-001"),
    ("Mantenimiento preventivo PC",       Decimal("20.00"), Decimal("5.00"),  "Servicio",         999, "SVC-002"),
    ("Formateo + instalación antivirus",  Decimal("30.00"), Decimal("5.00"),  "Servicio",         999, "SVC-003"),
    ("Instalación sistema operativo",     Decimal("25.00"), Decimal("5.00"),  "Servicio",         999, "SVC-004"),
    ("Configuración red / wifi",          Decimal("15.00"), Decimal("2.00"),  "Servicio",         999, "SVC-005"),
    ("Servicio y limpieza de impresora",  Decimal("18.00"), Decimal("3.00"),  "Servicio",         999, "SVC-006"),
    ("Recuperación de datos",             Decimal("40.00"), Decimal("5.00"),  "Servicio",         999, "SVC-007"),

    # ── Reparaciones ───────────────────────────────────────────────────
    ("Cambio de batería laptop",          Decimal("45.00"), Decimal("18.00"), "Reparación",       30,  "REP-001"),
    ("Cambio de teclado laptop",          Decimal("40.00"), Decimal("15.00"), "Reparación",       20,  "REP-002"),
    ("Reparación pantalla laptop",        Decimal("90.00"), Decimal("45.00"), "Reparación",       15,  "REP-003"),
    ("Cambio pasta térmica + limpieza",   Decimal("22.00"), Decimal("4.00"),  "Reparación",       50,  "REP-004"),
    ("Reparación cargador laptop",        Decimal("20.00"), Decimal("8.00"),  "Reparación",       30,  "REP-005"),
    ("Cambio disco duro por SSD",         Decimal("55.00"), Decimal("25.00"), "Reparación",       20,  "REP-006"),

    # ── Accesorios y repuestos ─────────────────────────────────────────
    ("Mouse inalámbrico",                 Decimal("12.00"), Decimal("6.00"),  "Producto",         25,  "ACC-001"),
    ("Teclado USB",                       Decimal("15.00"), Decimal("7.00"),  "Producto",         20,  "ACC-002"),
    ("Audífonos Bluetooth",               Decimal("18.00"), Decimal("8.00"),  "Producto",         15,  "ACC-003"),
    ("Cable HDMI 1.5m",                   Decimal("6.00"),  Decimal("2.50"),  "Producto",         30,  "ACC-004"),
    ("Hub USB 4 puertos",                 Decimal("9.00"),  Decimal("4.00"),  "Producto",         20,  "ACC-005"),
    ("Memoria USB 32GB",                  Decimal("8.00"),  Decimal("3.50"),  "Producto",         25,  "ACC-006"),
    ("Pasta térmica (tubo)",              Decimal("4.00"),  Decimal("1.50"),  "Producto",         40,  "ACC-007"),
    ("Tóner HP 85A",                      Decimal("28.00"), Decimal("14.00"), "Producto",         15,  "ACC-008"),
    ("Cartucho tinta Canon color",        Decimal("14.00"), Decimal("7.00"),  "Producto",         15,  "ACC-009"),
    ("Memoria RAM 8GB DDR4",              Decimal("38.00"), Decimal("20.00"), "Producto",         10,  "ACC-010"),
    ("Cable USB-C 1m",                    Decimal("3.50"),  Decimal("1.20"),  "Producto",         40,  "ACC-011"),
    ("Adaptador HDMI-VGA",                Decimal("8.00"),  Decimal("3.00"),  "Producto",         15,  "ACC-012"),
    ("Batería laptop genérica",           Decimal("38.00"), Decimal("18.00"), "Producto",         12,  "ACC-013"),

    # ── Papelería ──────────────────────────────────────────────────────
    ("Impresión B/N (por hoja)",          Decimal("0.05"),  Decimal("0.01"),  "Papelería",        9999, "PAP-001"),
    ("Impresión a color (por hoja)",      Decimal("0.25"),  Decimal("0.08"),  "Papelería",        9999, "PAP-002"),
    ("Copia de documento (por hoja)",     Decimal("0.10"),  Decimal("0.02"),  "Papelería",        9999, "PAP-003"),
    ("Anillado de documento",             Decimal("2.50"),  Decimal("0.80"),  "Papelería",        500,  "PAP-004"),
    ("Plastificado A4",                   Decimal("1.50"),  Decimal("0.40"),  "Papelería",        500,  "PAP-005"),
    ("Escaneado de documento",            Decimal("0.50"),  Decimal("0.05"),  "Papelería",        9999, "PAP-006"),
    ("Ayuda trámite IESS / SRI",          Decimal("5.00"),  Decimal("0.00"),  "Papelería",        9999, "PAP-007"),
    ("Impresión de foto 10x15",           Decimal("0.75"),  Decimal("0.20"),  "Papelería",        9999, "PAP-008"),

    # ── Recargas y pagos ───────────────────────────────────────────────
    ("Recarga celular $5",                Decimal("5.00"),  Decimal("4.80"),  "Recargas y Pagos", 9999, "REC-001"),
    ("Recarga celular $10",               Decimal("10.00"), Decimal("9.70"),  "Recargas y Pagos", 9999, "REC-002"),
    ("Recarga celular $15",               Decimal("15.00"), Decimal("14.60"), "Recargas y Pagos", 9999, "REC-003"),
    ("Paquete internet $15",              Decimal("15.00"), Decimal("14.50"), "Recargas y Pagos", 9999, "REC-004"),
    ("Pago servicio IESS",                Decimal("2.50"),  Decimal("0.00"),  "Recargas y Pagos", 9999, "REC-005"),
    ("Pago matrícula vehicular",          Decimal("3.00"),  Decimal("0.00"),  "Recargas y Pagos", 9999, "REC-006"),
    ("Pago de peaje",                     Decimal("1.50"),  Decimal("0.00"),  "Recargas y Pagos", 9999, "REC-007"),

    # ── Chucherías / regalos ───────────────────────────────────────────
    ("Globos surtidos x10",               Decimal("2.00"),  Decimal("0.80"),  "Chucherías",       100,  "CHU-001"),
    ("Cotillón cumpleaños",               Decimal("5.00"),  Decimal("2.00"),  "Chucherías",       50,   "CHU-002"),
    ("Piñata mediana",                    Decimal("8.00"),  Decimal("3.50"),  "Chucherías",       30,   "CHU-003"),
    ("Vela decorativa cumpleaños",        Decimal("1.50"),  Decimal("0.50"),  "Chucherías",       80,   "CHU-004"),
    ("Papel de regalo (hoja)",            Decimal("0.50"),  Decimal("0.15"),  "Chucherías",       200,  "CHU-005"),
]

# Egresos operativos del mes (para que la caja tenga movimientos)
EGRESOS_DEMO = [
    ("Compra resma de papel A4 x5",    Decimal("22.50"),  "purchase", 28),
    ("Tóner HP 85A (reposición)",       Decimal("55.00"),  "purchase", 20),
    ("Internet local mensual",          Decimal("30.00"),  "other",    25),
    ("Cartucho tinta Canon (reposición)",Decimal("28.00"), "purchase", 15),
    ("Suministros de limpieza",         Decimal("12.00"),  "other",    10),
    ("Recarga saldo distribuidora",     Decimal("100.00"), "purchase",  5),
]


class Command(BaseCommand):
    help = "Genera datos demo para presentación de tesis (productos, ventas recientes, caja)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema", default="magic_world",
            help="Schema del tenant a poblar (default: magic_world)",
        )
        parser.add_argument(
            "--ventas", type=int, default=150,
            help="Número de ventas recientes a generar (default: 150)",
        )
        parser.add_argument(
            "--dias", type=int, default=60,
            help="Rango de días hacia atrás para distribuir las ventas (default: 60)",
        )

    def handle(self, *args, **options):
        from django_tenants.utils import schema_context

        schema = options["schema"]
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n🌱  Sembrando datos demo en schema: '{schema}'\n"
        ))
        with schema_context(schema):
            self._run(options["ventas"], options["dias"])

    # ──────────────────────────────────────────────────────────────────
    def _run(self, n_ventas: int, n_dias: int):
        from apps.modules.inventory.models import Category, Product, Shelf
        from apps.modules.sales.models import Venta, VentaItem
        from apps.modules.cash_management.models import CashSession, CashMovement

        random.seed(42)  # reproducible

        # ── 1. Verificar si ya está sembrado ──────────────────────────
        if VentaItem.objects.exists():
            self.stdout.write(self.style.WARNING(
                "⚠️  Ya existen ítems de venta en este schema.\n"
                "   Para volver a sembrar, elimina los VentaItem existentes primero.\n"
                "   Omitiendo creación de ventas — solo actualizando catálogo y caja.\n"
            ))
            n_ventas = 0

        # ── 2. Perchas ────────────────────────────────────────────────
        self.stdout.write("  📦  Creando perchas...")
        perchas = [
            ("Vitrina Principal",   "Entrada del local — productos a la vista"),
            ("Servicio Técnico",    "Área de trabajo / taller"),
            ("Bodega",              "Almacén trasero"),
        ]
        shelf_objs = []
        for nombre, loc in perchas:
            s, _ = Shelf.objects.get_or_create(name=nombre, defaults={"location": loc})
            shelf_objs.append(s)
        self.stdout.write(f"     ✅  {len(shelf_objs)} perchas")

        # ── 3. Categorías ─────────────────────────────────────────────
        self.stdout.write("  🏷️   Creando categorías...")
        cat_names = ["Servicio", "Reparación", "Producto",
                     "Papelería", "Recargas y Pagos", "Chucherías"]
        cat_map = {}
        for name in cat_names:
            c, _ = Category.objects.get_or_create(name=name)
            cat_map[name] = c
        self.stdout.write(f"     ✅  {len(cat_map)} categorías")

        # ── 4. Productos ──────────────────────────────────────────────
        self.stdout.write("  🖥️   Creando productos...")
        prod_map: dict[str, Product] = {}
        shelves_cycle = [shelf_objs[0], shelf_objs[1], shelf_objs[0], shelf_objs[2]]
        for i, (nombre, precio, costo, cat_nombre, stock, sku) in enumerate(CATALOGO):
            prod, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name":      nombre,
                    "price":     precio,
                    "cost":      costo,
                    "category":  cat_map[cat_nombre],
                    "stock":     stock,
                    "stock_min": 5,
                    "shelf":     shelves_cycle[i % len(shelves_cycle)],
                    "is_active": True,
                },
            )
            prod_map[cat_nombre] = prod_map.get(cat_nombre) or prod  # primer producto por cat
            prod_map[nombre] = prod
        self.stdout.write(f"     ✅  {len(CATALOGO)} productos")

        # Agrupaciones para generar ventas realistas
        def prods_de(cat):
            return [Product.objects.get(sku=sku)
                    for _, _, _, c, _, sku in CATALOGO if c == cat]

        p_servicio   = prods_de("Servicio")
        p_reparacion = prods_de("Reparación")
        p_accesorios = prods_de("Producto")
        p_papeleria  = prods_de("Papelería")
        p_recargas   = prods_de("Recargas y Pagos")
        p_chucherias = prods_de("Chucherías")

        # ── 5. Ventas recientes con ítems ─────────────────────────────
        if n_ventas > 0:
            self.stdout.write(f"  🛍️   Generando {n_ventas} ventas "
                              f"(últimos {n_dias} días)...")

            import holidays as hlib
            hoy = date.today()
            ec_holidays = set()
            for yr in range(hoy.year - 1, hoy.year + 1):
                ec_holidays |= set(hlib.country_holidays("EC", years=[yr]).keys())

            metodos = ["efectivo"] * 6 + ["transferencia"] * 2 + ["deuna"] + ["tarjeta"]

            # Tipos de venta con pesos (frecuencia real del negocio)
            tipos  = ["papeleria", "recarga", "accesorio", "servicio", "reparacion", "chucheria"]
            pesos  = [0.32,        0.25,      0.20,        0.13,       0.07,         0.03]

            ventas_creadas = 0
            for _ in range(n_ventas):
                # Más ventas en días recientes (distribución triangular)
                dias_atras = int(random.triangular(0, n_dias, 3))
                fecha = hoy - timedelta(days=dias_atras)
                tipo  = random.choices(tipos, pesos)[0]

                items_data: list[tuple[Product, int]] = []  # (producto, cantidad)

                if tipo == "papeleria":
                    # Impresiones: muchas unidades, precio bajo
                    for p in random.sample(p_papeleria, k=min(2, len(p_papeleria))):
                        if "hoja" in p.name.lower() or "impresión" in p.name.lower() or "copia" in p.name.lower():
                            qty = random.randint(10, 80)
                        else:
                            qty = random.randint(1, 3)
                        items_data.append((p, qty))

                elif tipo == "recarga":
                    for p in random.sample(p_recargas, k=random.randint(1, 2)):
                        items_data.append((p, 1))

                elif tipo == "accesorio":
                    for p in random.sample(p_accesorios, k=random.randint(1, 2)):
                        items_data.append((p, random.randint(1, 2)))

                elif tipo == "servicio":
                    items_data.append((random.choice(p_servicio), 1))
                    # 25% incluye accesorio adicional
                    if random.random() < 0.25:
                        items_data.append((random.choice(p_accesorios), 1))

                elif tipo == "reparacion":
                    items_data.append((random.choice(p_reparacion), 1))
                    # 30% incluye repuesto adicional
                    if random.random() < 0.30:
                        items_data.append((random.choice(p_accesorios), 1))

                else:  # chucheria
                    for p in random.sample(p_chucherias, k=random.randint(1, 3)):
                        items_data.append((p, random.randint(1, 4)))

                if not items_data:
                    continue

                venta = Venta.objects.create(
                    fecha_venta=fecha,
                    metodo_pago=random.choice(metodos),
                    es_feriado=(fecha in ec_holidays),
                    # mes, dia_semana, es_fin_de_semana los setea Venta.save()
                )

                for prod, qty in items_data:
                    VentaItem.objects.create(
                        venta=venta,
                        product=prod,
                        description=prod.name,
                        quantity=qty,
                        unit_price=prod.price,
                        # subtotal lo calcula VentaItem.save()
                    )

                venta.recalculate_total()
                ventas_creadas += 1

            self.stdout.write(f"     ✅  {ventas_creadas} ventas creadas")
        else:
            ventas_creadas = 0

        # ── 6. CashSession para hoy ───────────────────────────────────
        self.stdout.write("  💰  Configurando sesión de caja para hoy...")
        session, created = CashSession.objects.get_or_create(
            date=date.today(),
            defaults={"opening_amount": Decimal("50.00")},
        )
        if created:
            self.stdout.write("     ✅  Sesión creada — apertura: $50.00")
        else:
            self.stdout.write("     ℹ️   Sesión de hoy ya existía")

        # ── 7. CashMovements de ingresos (ventas recientes) ───────────
        self.stdout.write("  💵  Sincronizando movimientos de ingresos...")
        ingresos_sync = 0
        for venta in Venta.objects.filter(fecha_venta__gte=date.today() - timedelta(days=7)):
            _, created_cm = CashMovement.objects.get_or_create(
                description=f"Venta #{venta.id}",
                defaults={
                    "type":     "income",
                    "category": "sale",
                    "amount":   venta.total,
                    "date":     venta.fecha_venta,
                },
            )
            if created_cm:
                ingresos_sync += 1
        self.stdout.write(f"     ✅  {ingresos_sync} movimientos de ingreso nuevos")

        # ── 8. CashMovements de egresos operativos ────────────────────
        self.stdout.write("  📋  Creando egresos operativos del mes...")
        egresos_creados = 0
        for desc, amount, category, dias_atras in EGRESOS_DEMO:
            _, created_cm = CashMovement.objects.get_or_create(
                description=desc,
                defaults={
                    "type":     "expense",
                    "category": category,
                    "amount":   amount,
                    "date":     date.today() - timedelta(days=dias_atras),
                },
            )
            if created_cm:
                egresos_creados += 1
        self.stdout.write(f"     ✅  {egresos_creados} egresos operativos")

        # ── Resumen final ─────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f"\n{'─'*50}\n"
            f"✅  Seed completado\n"
            f"{'─'*50}\n"
            f"  Perchas:          3\n"
            f"  Categorías:       {len(cat_map)}\n"
            f"  Productos:        {len(CATALOGO)}\n"
            f"  Ventas nuevas:    {ventas_creadas}\n"
            f"  CashSession hoy:  ✅\n"
            f"  Egresos del mes:  {egresos_creados}\n"
            f"{'─'*50}\n\n"
            f"Prueba el chatbot con:\n"
            f'  "¿cuánto vendimos esta semana?"\n'
            f'  "¿cuáles son los productos más vendidos?"\n'
            f'  "¿cuánto vamos a vender la próxima semana?"\n'
            f'  "¿cómo está el balance de caja?"\n'
        ))
