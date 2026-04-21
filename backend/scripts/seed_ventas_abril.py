"""
Script: seed_ventas_abril.py
Rellena ventas desde la última fecha registrada hasta 2026-04-16
para los tenants magic_world y papeleria.
También crea/actualiza los CashMovements diarios para el balance de caja.

Uso:
  cd backend
  DJANGO_SETTINGS_MODULE=config.settings python scripts/seed_ventas_abril.py
"""

import os
import sys
import random
import django
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django_tenants.utils import schema_context

random.seed(99)

FECHA_FIN = date(2026, 4, 16)
METODOS_PAGO = ["efectivo", "efectivo", "efectivo", "tarjeta", "transferencia", "deuna"]

# Semana Santa — ventas muy reducidas
FERIADOS = {
    date(2026, 4, 10),  # Viernes Santo
    date(2026, 4, 11),  # Sábado Santo
    date(2026, 4, 12),  # Domingo de Pascua
}


# ── Reglas de cantidad por rango de precio ─────────────────────────────────
def cantidad_para_precio(precio: float) -> int:
    """Reproduce el comportamiento real: artículos baratos se compran en volumen."""
    if precio < 0.10:    # hojas B/N $0.05
        return random.randint(5, 30)
    if precio < 0.30:    # hojas color, copia $0.10-$0.25
        return random.randint(3, 15)
    if precio < 1.00:    # escaneado, foto, papel regalo
        return random.randint(1, 5)
    if precio < 3.00:    # plastificado, pagos, anillado
        return random.randint(1, 3)
    return 1             # productos $3+ → siempre 1 unidad


# ── Selección ponderada de productos ──────────────────────────────────────
def elegir_productos(productos: list, n: int) -> list:
    """
    Pondera la selección: 55% productos baratos (<$3), 30% medios ($3-$15), 15% altos (>$15).
    Excluye productos sin stock.
    """
    baratos  = [p for p in productos if float(p["price"]) <  3.0  and p["stock"] > 0]
    medios   = [p for p in productos if 3.0 <= float(p["price"]) <= 15.0 and p["stock"] > 0]
    caros    = [p for p in productos if 15.0 < float(p["price"]) <= 50.0 and p["stock"] > 0]

    pool = []
    pool += random.choices(baratos, k=min(len(baratos), 6)) if baratos else []
    pool += random.choices(medios,  k=min(len(medios),  3)) if medios  else []
    pool += random.choices(caros,   k=min(len(caros),   1)) if caros   else []

    if not pool:
        pool = [p for p in productos if p["stock"] > 0]

    # Evitar duplicados en la misma transacción
    seleccion, vistos = [], set()
    random.shuffle(pool)
    for p in pool:
        if p["id"] not in vistos:
            seleccion.append(p)
            vistos.add(p["id"])
        if len(seleccion) >= n:
            break
    return seleccion[:n]


# ── Número de ventas según día ─────────────────────────────────────────────
def n_ventas_dia(schema: str, fecha: date) -> int:
    dow = fecha.weekday()
    es_feriado = fecha in FERIADOS

    if schema == "magic_world":
        if es_feriado:            return random.randint(2, 4)
        if dow == 6:              return random.randint(3, 6)   # domingo
        if dow == 5:              return random.randint(6, 10)  # sábado
        return random.randint(8, 13)                            # lun-vie
    else:  # papeleria
        if es_feriado:            return random.randint(1, 3)
        if dow == 6:              return random.randint(2, 5)
        if dow == 5:              return random.randint(4, 7)
        return random.randint(5, 10)


# ── Items por transacción ──────────────────────────────────────────────────
def n_items_transaccion() -> int:
    """La mayoría de ventas son de 1-2 productos."""
    return random.choices([1, 2, 3], weights=[60, 30, 10])[0]


# ── Seed por tenant ────────────────────────────────────────────────────────
def seed_tenant(schema_name: str):
    with schema_context(schema_name):
        from apps.modules.inventory.models import Product
        from apps.modules.sales.models import Venta, VentaItem
        from apps.modules.cash_management.models import CashMovement

        productos = list(
            Product.objects.filter(is_active=True, stock__gt=0)
            .values("id", "name", "price", "stock")
        )
        if not productos:
            print(f"  ⚠  {schema_name}: sin productos. Saltando.")
            return

        ultima = Venta.objects.order_by("-fecha_venta").first()
        fecha_inicio = (ultima.fecha_venta + timedelta(days=1)) if ultima else date(2026, 3, 27)

        if fecha_inicio > FECHA_FIN:
            print(f"  ✓  {schema_name}: ya está al día (última: {ultima.fecha_venta})")
            return

        total_ventas = 0
        total_monto  = Decimal("0.00")

        # Mapa local de stock para no releer BD en cada venta
        stock_local = {p["id"]: p["stock"] for p in productos}

        # Acumulado diario para CashMovements
        ventas_por_dia = {}

        fecha = fecha_inicio
        while fecha <= FECHA_FIN:
            dow = fecha.weekday()
            es_fin_semana = dow >= 5
            es_feriado = fecha in FERIADOS
            monto_dia = Decimal("0.00")
            caros_usados_hoy = 0  # máx 1 ítem caro (>$15) por día

            for _ in range(n_ventas_dia(schema_name, fecha)):
                n_items = n_items_transaccion()
                # Filtrar productos con stock disponible localmente
                # Si ya se usó un caro hoy, excluirlos del pool
                if caros_usados_hoy >= 1:
                    disponibles = [p for p in productos if stock_local.get(p["id"], 0) > 0 and float(p["price"]) <= 15.0]
                else:
                    disponibles = [p for p in productos if stock_local.get(p["id"], 0) > 0]
                if not disponibles:
                    disponibles = [p for p in productos if stock_local.get(p["id"], 0) > 0]
                if not disponibles:
                    break
                items_elegidos = elegir_productos(disponibles, n_items)

                venta = Venta(
                    fecha_venta=fecha,
                    total=Decimal("0.00"),
                    metodo_pago=random.choice(METODOS_PAGO),
                    es_feriado=es_feriado,
                    es_fin_de_semana=es_fin_semana,
                )
                venta.save()

                subtotal_venta = Decimal("0.00")
                for prod in items_elegidos:
                    precio = Decimal(str(prod["price"]))
                    qty    = cantidad_para_precio(float(precio))
                    # No exceder stock disponible
                    qty    = min(qty, stock_local[prod["id"]])
                    if qty == 0:
                        continue
                    subtotal = precio * qty

                    VentaItem.objects.create(
                        venta=venta,
                        product_id=prod["id"],
                        description=prod["name"],
                        quantity=qty,
                        unit_price=precio,
                        subtotal=subtotal,
                    )
                    subtotal_venta += subtotal
                    stock_local[prod["id"]] = max(0, stock_local[prod["id"]] - qty)
                    if float(prod["price"]) > 15.0:
                        caros_usados_hoy += 1

                if subtotal_venta == 0:
                    venta.delete()
                    continue

                venta.total = subtotal_venta
                venta.save(update_fields=["total"])
                total_monto  += subtotal_venta
                total_ventas += 1
                monto_dia    += subtotal_venta

            if monto_dia > 0:
                ventas_por_dia[fecha] = monto_dia

            fecha += timedelta(days=1)

        # Actualizar stock real en BD
        for pid, stk in stock_local.items():
            Product.objects.filter(id=pid).update(stock=stk)

        # Crear CashMovements diarios
        cash_creados = 0
        for fec, monto in ventas_por_dia.items():
            # Evitar duplicados
            existe = CashMovement.objects.filter(
                date=fec,
                category='sale',
                type='income',
            ).exists()
            if not existe:
                CashMovement.objects.create(
                    date=fec,
                    amount=monto,
                    type='income',
                    category='sale',
                    description=f'Ventas del día {fec.strftime("%d/%m/%Y")}',
                )
                cash_creados += 1

        dias = (FECHA_FIN - fecha_inicio).days + 1
        print(f"  ✓  {schema_name}: {total_ventas} ventas en {dias} días "
              f"({fecha_inicio} → {FECHA_FIN}) | total: ${total_monto:.2f} "
              f"| prom/día: ${float(total_monto)/dias:.2f} "
              f"| cash movements: +{cash_creados}")


if __name__ == "__main__":
    print("=" * 65)
    print(f"  Seed ventas hasta {FECHA_FIN}")
    print("=" * 65)
    seed_tenant("magic_world")
    seed_tenant("papeleria")
    print("=" * 65)
    print("  Listo.")
