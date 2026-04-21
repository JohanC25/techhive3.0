"""
Script: seed_compras_tickets.py
Agrega órdenes de compra y tickets de servicio técnico de ejemplo
para los tenants magic_world y papeleria.

Uso:
  cd backend
  DJANGO_SETTINGS_MODULE=config.settings python scripts/seed_compras_tickets.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django_tenants.utils import schema_context

# ─── Datos magic_world ────────────────────────────────────────────────────────

SUPPLIERS_MAGIC = [
    {"name": "Tecnología Global S.A.", "ruc": "1791234560001", "email": "ventas@tecglobal.ec", "phone": "022345678"},
    {"name": "Distribuidora InnoTech", "ruc": "1791234561001", "email": "pedidos@innotech.ec",  "phone": "022456789"},
    {"name": "Importaciones Digital Cía.", "ruc": "1791234562001", "email": "info@impdigital.ec",  "phone": "022567890"},
]

PURCHASES_MAGIC = [
    # (días_atras, proveedor_idx, status, items)
    (45, 0, "received", [
        ("Laptop HP 15.6 i5", 2, Decimal("450.00")),
        ("Mouse inalámbrico Logitech", 10, Decimal("18.00")),
        ("Teclado USB estándar", 5, Decimal("12.00")),
    ]),
    (30, 1, "received", [
        ("Memoria RAM 8GB DDR4", 8, Decimal("35.00")),
        ("Disco SSD 480GB", 4, Decimal("55.00")),
        ("Cable HDMI 1.5m", 15, Decimal("5.50")),
    ]),
    (20, 2, "received", [
        ("Hub USB 4 puertos", 10, Decimal("8.00")),
        ("Audífonos con micrófono", 6, Decimal("22.00")),
        ("Memoria USB 32GB", 12, Decimal("7.50")),
    ]),
    (10, 0, "received", [
        ("Laptop Lenovo IdeaPad i3", 3, Decimal("380.00")),
        ("Pasta térmica tubo", 8, Decimal("3.50")),
        ("Pad mouse grande", 10, Decimal("6.00")),
    ]),
    (5, 1, "pending", [
        ("Monitor LED 22''", 2, Decimal("130.00")),
        ("Teclado inalámbrico Bluetooth", 4, Decimal("28.00")),
        ("Webcam HD 1080p", 3, Decimal("32.00")),
    ]),
    (2, 2, "pending", [
        ("Disco SSD 1TB", 2, Decimal("90.00")),
        ("Cable USB-C a USB-A", 20, Decimal("3.00")),
        ("Protector de pantalla 15.6", 5, Decimal("8.00")),
    ]),
]

TICKETS_MAGIC = [
    # (días_atras, cliente, teléfono, dispositivo, problema, diagnóstico, solución, costo_est, costo_final, status, prioridad, dias_para_entrega)
    (30, "Carlos Mendoza",   "0987654321", "Laptop HP 15.6",      "No enciende",                  "Falla en placa base, capacitor dañado",    "Reemplazo de capacitor y limpieza",       Decimal("60.00"),  Decimal("55.00"),  "delivered",    "high",   0),
    (25, "Ana Torres",       "0976543210", "PC de escritorio",    "Pantalla azul frecuente",       "Memoria RAM con sectores defectuosos",     "Reemplazo de módulo RAM 8GB",             Decimal("45.00"),  Decimal("40.00"),  "delivered",    "medium", 0),
    (20, "Luis Paredes",     "0965432109", "Laptop Lenovo",       "Teclado no funciona",           "Conector de teclado desprendido",          "Reconexión y limpieza de contactos",     Decimal("30.00"),  Decimal("25.00"),  "delivered",    "low",    0),
    (15, "María González",   "0954321098", "Laptop Asus",         "Batería no carga",              "Batería agotada, ciclos al límite",        "Reemplazo de batería original",           Decimal("70.00"),  Decimal("65.00"),  "delivered",    "medium", 0),
    (12, "Pedro Álvarez",    "0943210987", "Impresora Epson L3150","No imprime, error de tinta",   "Cabezal obstruido, almohadillas llenas",   "Limpieza de cabezal y reset almohadillas",Decimal("35.00"),  Decimal("30.00"),  "completed",    "medium", 0),
    (8,  "Sofía Castillo",   "0932109876", "Laptop Dell 14",      "Se apaga solo al poco rato",    "Pasta térmica seca, ventilador bloqueado", "Limpieza y cambio de pasta térmica",      Decimal("40.00"),  Decimal("35.00"),  "completed",    "high",   0),
    (6,  "Jorge Romero",     "0921098765", "Laptop HP Pavilion",  "Pantalla rota",                 "LCD dañado por golpe",                     "Reemplazo de pantalla 15.6''",            Decimal("95.00"),  None,              "in_progress",  "high",   3),
    (4,  "Valeria Mora",     "0910987654", "PC Escritorio",       "Muy lento, tarda en iniciar",   "HDD con sectores dañados, 80% fragmentado","Migración a SSD + reinstalación Windows", Decimal("80.00"),  None,              "in_progress",  "medium", 4),
    (2,  "Roberto Silva",    "0909876543", "Laptop Toshiba",      "No detecta WiFi",               "Tarjeta de red defectuosa",                None,                                      Decimal("50.00"),  None,              "pending",      "medium", 5),
    (1,  "Diana Flores",     "0898765432", "Laptop Acer Aspire",  "Teclado mojado, varias teclas no responden", "Daño por líquido en membrana de teclado", None,                          Decimal("45.00"),  None,              "pending",      "urgent", 3),
]

# ─── Datos papeleria ──────────────────────────────────────────────────────────

SUPPLIERS_PAP = [
    {"name": "Suministros Papelería Express", "ruc": "1791234563001", "email": "ventas@papexpress.ec", "phone": "022678901"},
    {"name": "Distribuidora Escolar Cía.",     "ruc": "1791234564001", "email": "pedidos@distescolar.ec","phone": "022789012"},
]

PURCHASES_PAP = [
    (40, 0, "received", [
        ("Resma papel bond A4 75g (500 hojas)", 20, Decimal("4.50")),
        ("Cartucho tinta Canon negra PG-745", 10, Decimal("12.00")),
        ("Cartucho tinta Canon color CL-746", 8, Decimal("14.00")),
    ]),
    (25, 1, "received", [
        ("Anillados plásticos 14mm x100", 5, Decimal("6.00")),
        ("Fundas plásticas tamaño oficio x100", 8, Decimal("3.50")),
        ("Espiral metálico 3/8 x100", 4, Decimal("8.00")),
    ]),
    (15, 0, "received", [
        ("Tóner HP LaserJet 85A", 3, Decimal("32.00")),
        ("Papel fotográfico glossy A4 x50", 6, Decimal("5.50")),
        ("Laminado A4 x100 hojas", 4, Decimal("9.00")),
    ]),
    (7, 1, "received", [
        ("Resma papel bond A4 75g (500 hojas)", 15, Decimal("4.50")),
        ("Cinta adhesiva transparente x12", 5, Decimal("2.50")),
        ("Clips metálicos x100", 10, Decimal("1.20")),
    ]),
    (3, 0, "pending", [
        ("Cartucho tinta Epson T544 negro", 6, Decimal("8.00")),
        ("Cartucho tinta Epson T544 color", 4, Decimal("9.50")),
        ("Resma papel bond A4 75g (500 hojas)", 10, Decimal("4.50")),
    ]),
]

TICKETS_PAP = [
    (22, "Fernanda Castro",  "0887654321", "Impresora Epson L575", "No imprime desde WiFi",         "Driver desactualizado, IP dinámica",       "Actualización driver + IP fija",          Decimal("15.00"),  Decimal("12.00"),  "delivered",    "low",    0),
    (18, "Andrés Vega",      "0876543210", "Laptop HP 14",        "Bisagra rota",                   "Bisagra izquierda fracturada por uso",     "Reemplazo de bisagra + carcasa ajuste",   Decimal("40.00"),  Decimal("38.00"),  "delivered",    "medium", 0),
    (14, "Carmen Suárez",    "0865432109", "PC Escritorio",       "Sin imagen en monitor",          "Cable VGA oxidado, GPU con polvo",         "Limpieza GPU + reemplazo cable VGA",      Decimal("25.00"),  Decimal("20.00"),  "delivered",    "low",    0),
    (9,  "Marco Espinoza",   "0854321098", "Laptop Lenovo E14",   "Carga lenta y se desconecta",    "Puerto de carga con contactos oxidados",   "Limpieza de puerto y reemplazo cargador", Decimal("35.00"),  Decimal("30.00"),  "completed",    "medium", 0),
    (5,  "Isabella Reyes",   "0843210987", "Impresora Canon MG",  "Atasco de papel frecuente",      "Rodillo de arrastre desgastado",           "Reemplazo de rodillo de arrastre",        Decimal("28.00"),  None,              "in_progress",  "medium", 2),
    (2,  "Santiago Mora",    "0832109876", "Laptop Asus VivoBook","Pantalla parpadea",               "Conector LVDS flojo",                      None,                                      Decimal("50.00"),  None,              "pending",      "high",   4),
]


def seed_tenant(schema_name: str, suppliers_data, purchases_data, tickets_data):
    with schema_context(schema_name):
        from apps.modules.purchases.models import Purchase, PurchaseItem, Supplier
        from apps.modules.technical_service.models import ServiceTicket

        hoy = date.today()

        # ── Proveedores ──────────────────────────────────────────────────────
        suppliers = []
        for s in suppliers_data:
            obj, _ = Supplier.objects.get_or_create(
                ruc=s["ruc"],
                defaults={
                    "name": s["name"],
                    "email": s["email"],
                    "phone": s["phone"],
                    "is_active": True,
                }
            )
            suppliers.append(obj)

        # ── Compras ──────────────────────────────────────────────────────────
        compras_creadas = 0
        for dias_atras, sup_idx, status, items in purchases_data:
            fecha = hoy - timedelta(days=dias_atras)
            total = sum(qty * precio for _, qty, precio in items)

            purchase = Purchase.objects.create(
                supplier=suppliers[sup_idx],
                date=fecha,
                status=status,
                total=total,
                notes="",
            )
            for desc, qty, unit_price in items:
                PurchaseItem.objects.create(
                    purchase=purchase,
                    description=desc,
                    quantity=qty,
                    unit_price=unit_price,
                    subtotal=qty * unit_price,
                )
            compras_creadas += 1

        # ── Tickets ──────────────────────────────────────────────────────────
        tickets_creados = 0
        for row in tickets_data:
            (dias_atras, cliente, telefono, dispositivo, problema,
             diagnostico, solucion, costo_est, costo_final,
             status, prioridad, dias_entrega) = row

            received_at = hoy - timedelta(days=dias_atras)
            promised_at = received_at + timedelta(days=dias_entrega + 3)
            completed_at = None
            if status in ("completed", "delivered"):
                completed_at = received_at + timedelta(days=dias_entrega + 1)

            ServiceTicket.objects.create(
                client_name=cliente,
                client_phone=telefono,
                device=dispositivo,
                problem=problema,
                diagnosis=diagnostico or "",
                solution=solucion or "",
                estimated_cost=costo_est,
                final_cost=costo_final,
                status=status,
                priority=prioridad,
                received_at=received_at,
                promised_at=promised_at,
                completed_at=completed_at,
            )
            tickets_creados += 1

        print(f"  ✓  {schema_name}: {compras_creadas} compras, {tickets_creados} tickets creados")


if __name__ == "__main__":
    print("=" * 55)
    print("  Seed compras y tickets de servicio técnico")
    print("=" * 55)
    seed_tenant("magic_world", SUPPLIERS_MAGIC, PURCHASES_MAGIC, TICKETS_MAGIC)
    seed_tenant("papeleria",   SUPPLIERS_PAP,   PURCHASES_PAP,   TICKETS_PAP)
    print("=" * 55)
    print("  Listo.")
