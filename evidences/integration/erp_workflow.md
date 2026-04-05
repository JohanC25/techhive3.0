# Flujos ERP — TechHive 3.0

Documentación de la integración entre módulos del sistema ERP:
ventas, inventario, compras, caja y servicio técnico.

---

## 1. Ciclo de venta completo

```
[Staff crea venta en SalesView.vue]
         │
         ▼ POST /api/sales/ventas/
         │  {fecha, metodo_pago, client, items: [{product, qty, unit_price}]}
         │
         ▼ VentaSerializer.create()
         │
         ├─ Por cada ítem:
         │   ├─ INSERT ventas_ventaitem (venta_id, product_id, qty, price, subtotal)
         │   └─ UPDATE inventory_product SET stock = stock - qty    ← descuento automático
         │
         ├─ UPDATE ventas_venta SET total = SUM(subtotales)         ← recalculate_total()
         │
         └─ Signal post_save →
              INSERT cash_movement(type='income', category='sale',
                                   amount=total, date=today)        ← caja automática
         │
         ▼ HTTP 201 — Venta registrada
```

**Tablas afectadas:**
- `ventas_venta` — cabecera de la venta
- `ventas_ventaitem` — líneas de ítems
- `inventory_product.stock` — decrementado
- `cash_movement` — ingreso registrado automáticamente

---

## 2. Ciclo de compra completo

```
[Staff crea orden de compra en PurchasesView.vue]
         │
         ▼ POST /api/purchases/purchases/
         │  {supplier, items: [{description, qty, unit_price}], notes}
         │  status inicial = "pending"
         │
         ▼ Purchase creada, sin afectar stock ni caja
         │
[Staff confirma recepción de mercancía]
         │
         ▼ PATCH /api/purchases/purchases/{id}/
         │  {status: "received"}
         │
         ▼ Signal pre_save (detecta cambio pending → received)
         │
         └─ INSERT cash_movement(type='expense', category='purchase',
                                 amount=purchase.total,
                                 description='Compra #ID — Proveedor ABC')
         │
         ▼ HTTP 200 — Compra recibida + egreso registrado en caja
```

**Nota:** El descuento de stock en compras no está automatizado — el staff actualiza
el stock manualmente desde la vista de inventario al recibir la mercancía.

---

## 3. Apertura y cierre de caja

```
[Staff abre turno — 8:00 AM]
         │
         ▼ GET /api/cash/sessions/today/  → 404 (no hay sesión)
         │
         ▼ Frontend muestra modal "Apertura de caja"
         │
         ▼ POST /api/cash/sessions/
         │  {opening_amount: 200.00}
         │
         ├─ INSERT cash_session(date=today, opened_by=user_id, opening_amount=200.00)
         │
         ▼ Sesión abierta → Frontend continúa

[Durante el día — transacciones automáticas]
         │
         ├─ Venta #1: +$45.00  → INSERT cash_movement(type='income', category='sale')
         ├─ Venta #2: +$120.00 → INSERT cash_movement(type='income', category='sale')
         ├─ Compra recibida: -$350.00 → INSERT cash_movement(type='expense', category='purchase')
         └─ Movimiento manual: +$50.00 → POST /api/cash/movements/ (staff lo registra)

[Staff consulta balance al final del día]
         │
         ▼ GET /api/cash/balance/
         │
         ├─ caja_inicial = cash_session.opening_amount = $200.00
         ├─ ingresos = SUM(cash_movement WHERE type='income' AND date=today) = $215.00
         ├─ egresos = SUM(cash_movement WHERE type='expense' AND date=today) = $350.00
         └─ caja_final = $200.00 + $215.00 - $350.00 = $65.00
```

---

## 4. Ticket de servicio técnico

```
[Cliente llega con equipo dañado]
         │
         ▼ Staff crea ticket en TicketsView.vue
         │
         ▼ POST /api/technical-service/tickets/
         │  {client: 5,                 ← usuario con role='client'
         │   device: "Laptop HP",
         │   serial_number: "SN12345",
         │   accessories: "Cargador",
         │   problem: "No enciende",
         │   estimated_cost: 80.00,
         │   priority: "high",
         │   promised_at: "2026-04-07"}
         │
         ├─ ServiceTicketSerializer._sync_client_fields() copia
         │  client.first_name + last_name, phone, email al ticket
         │  (para persistencia si el cliente es eliminado)
         │
         ▼ Ticket creado con status='pending'

[Staff actualiza diagnóstico y solución]
         │
         ▼ PATCH /api/technical-service/tickets/{id}/
         │  {diagnosis: "Placa base quemada",
         │   solution: "Cambio de placa base",
         │   final_cost: 95.00,
         │   status: "in_progress"}
         │
[Reparación completada]
         │
         ▼ PATCH /api/technical-service/tickets/{id}/
         │  {status: "completed",
         │   completed_at: "2026-04-07T15:30:00Z"}
         │
         ▼ Staff cobra al cliente → registra venta o movimiento de caja manual
```

**Estados del ticket:** `pending → in_progress → completed | cancelled`

---

## 5. Alertas de inventario bajo stock

```
[Sistema de alerta integrado]
         │
         ▼ GET /api/inventory/products/?low_stock=true
         │  (o chatbot: "que productos tienen stock bajo")
         │
         ├─ SELECT * FROM inventory_product
         │    WHERE stock <= stock_min AND is_active = TRUE
         │
         ▼ Productos con low_stock=True:
         │   {name: "Tóner HP 85A", stock: 2, stock_min: 5, low_stock: true}
         │
         ▼ Staff usa chatbot para recomendación:
         │   "que debo pedir al proveedor"
         │   → handle_recomendar_compra():
         │       1. Consulta productos con low_stock
         │       2. Llama predictor.forecast() para proyección de demanda
         │       3. Calcula cantidad sugerida a pedir
         │       4. Retorna lista priorizada
```

---

## 6. Dashboard de predicción en el frontend

```
[Staff abre DashboardView.vue]
         │
         ▼ GET /api/prediccion/?dias=7
         │
         ├─ predictor.py:forecast("magic_world", horizon=7)
         │   1. Query: ventas históricas últimos 90 días
         │   2. Build features_v22 (78 variables)
         │   3. Predict: magic_ratio_v22.pkl → blend → calibrar
         │   4. Return: [{fecha, prediccion}, ...]
         │
         ▼ Frontend renderiza gráfico de proyección
         │
         ▼ GET /api/sales/ventas/?fecha_venta=today
         │   → Ventas reales del día
         │
         ▼ Comparación: predicción vs real en el mismo gráfico
```

---

## Matriz de integración entre módulos

| Módulo origen | Módulo destino | Trigger | Tipo |
|---------------|----------------|---------|------|
| Ventas | Inventario | Crear venta | Automático — descuento de stock |
| Ventas | Caja | Crear venta | Signal post_save → CashMovement income |
| Compras | Caja | Recibir compra | Signal pre_save → CashMovement expense |
| Caja | — | — | Movimientos manuales vía POST /cash/movements/ |
| Predicción ML | Chatbot | intent=prediccion | handle_prediccion() llama predictor.forecast() |
| Predicción ML | Chatbot | intent=recomendar_compra | handle_recomendar_compra() llama forecast() |
| Predicción ML | Chatbot | intent=alerta_demanda | handle_alerta_demanda() llama forecast() |
| Servicio Técnico | Caja | Cobro al cliente (manual) | Staff registra pago como venta o movimiento |
| Inventario | Chatbot | intent=inventario_stock | handle_inventario_stock() consulta inventory_product |
