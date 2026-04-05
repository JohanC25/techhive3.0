# Flujos del Sistema — TechHive 3.0

Documentación de los flujos principales del sistema, desde la petición HTTP hasta la respuesta,
mostrando la integración entre componentes.

---

## Flujo 1 — Autenticación y acceso multi-tenant

```
Cliente HTTP
    │
    ▼
GET/POST http://magic.techhive.local:8000/api/...
    │
    ├── Host header: "magic.techhive.local"
    │
    ▼
TenantMainMiddleware (django-tenants)
    │  Consulta: SELECT schema_name FROM tenants_company
    │            JOIN tenants_domain ON domain = "magic.techhive.local"
    │  → Establece connection.schema_name = "magic_world"
    │  → request.tenant = <Company: Magic World>
    │
    ▼
ModuleAccessMiddleware
    │  Verifica: ¿El módulo requerido (por URL namespace) está habilitado para este tenant?
    │  Si no → HTTP 403
    │
    ▼
JWTAuthentication (djangorestframework_simplejwt)
    │  Verifica: Bearer token en header Authorization
    │  Decodifica: user_id, role, exp
    │  Si inválido/expirado → HTTP 401
    │
    ▼
IsAuthenticated / IsNotClient (permission classes)
    │  Si role=client intenta endpoint staff → HTTP 403
    │
    ▼
View / ViewSet (DRF)
    │  Todas las queries se ejecutan en schema "magic_world"
    │  connection.schema_name es seteado antes de cada request
    │
    ▼
Respuesta JSON
```

---

## Flujo 2 — Creación de venta (integración ERP completa)

```
POST /api/sales/ventas/
Body: {fecha, metodo_pago, client_id, items: [{product, qty, price}]}
    │
    ▼
VentaSerializer.validate()
    │  Valida campos, verifica que client existe
    │
    ▼
VentaSerializer.create()
    │
    ├── 1. Crea registro Venta (cabecera)
    │      INSERT INTO ventas_venta (fecha, metodo_pago, client_id, ...)
    │
    ├── 2. Por cada ítem en items[]:
    │      ├── Crea VentaItem
    │      │    INSERT INTO ventas_ventaitem (venta_id, product_id, qty, price, subtotal)
    │      └── Descuenta stock del producto
    │           UPDATE inventory_product SET stock = stock - qty WHERE id = product_id
    │
    ├── 3. Calcula total
    │      UPDATE ventas_venta SET total = SUM(item.subtotal) WHERE id = venta_id
    │
    └── 4. Signal post_save → CashMovement
           INSERT INTO cash_movement (type='income', category='sale',
                                     amount=venta.total, date=today,
                                     description='Venta #47')
    │
    ▼
HTTP 201 — Venta creada con ítems, total calculado y stock actualizado
```

---

## Flujo 3 — Chatbot staff con predicción ML

```
POST /api/chatbot/mensaje/
Body: {"mensaje": "prediccion de ventas", "session_id": "uuid"}
    │
    ▼
views.py:enviar_mensaje()
    │
    ├── Determina canal:
    │    es_cliente = (request.user.role == 'client')  → False → canal staff
    │
    ▼
router.py:detectar_intencion("prediccion de ventas")
    │  Evalúa regex patterns en orden de prioridad
    │  Pattern: r'predicci[oó]n|proyecci[oó]n|cuanto\s+vender[eé]'
    │  → intent = "prediccion"
    │
    ▼
handlers.py:ejecutar_intencion({"intent": "prediccion", ...})
    │
    ▼
handlers.py:handle_prediccion()
    │
    ├── 1. Obtiene tenant actual: connection.schema_name = "magic_world"
    │
    ├── 2. Llama al predictor:
    │    from apps.prediccion.predictor import get_predictor
    │    predictor = get_predictor()  # Singleton — carga PKLs una sola vez
    │    resultado = predictor.forecast(tenant_slug="magic_world", horizon=7)
    │
    ▼
predictor.py:forecast(tenant_slug, horizon)
    │
    ├── 1. Consulta historial de ventas del tenant (últimos 90 días mín.)
    │    SELECT fecha, SUM(total) as ventas
    │    FROM ventas_venta GROUP BY fecha ORDER BY fecha
    │
    ├── 2. Construye features_v22 (78 variables):
    │    - Lags (lag1…lag28) desde historial
    │    - Features climáticas (Meteostat API o cache)
    │    - Features de calendario (feriados Ecuador)
    │    - Rolling stats, EMAs, diferencias, regímenes
    │
    ├── 3. Genera predicciones:
    │    pred_ratio = magic_ratio_v22.predict(X)  ← pkl cargado en memoria
    │    pred_blend = 1.0 × pred_ratio + 0.0 × pred_direct + 0.0 × pred_global
    │
    ├── 4. Aplica expm1 para volver a escala original
    │
    ├── 5. Aplica calibración por segmento:
    │    mult = seg_mult["1_0"] if is_weekend else seg_mult["0_0"]
    │    pred_final = pred_blend × mult × global_mult
    │
    └── Retorna: [{"fecha": "2026-04-05", "prediccion": 142.50}, ...]
    │
    ▼
handlers.py formatea respuesta en texto legible
    │
    ▼
views.py guarda en ChatMessage (historial)
    │
    ▼
HTTP 200: {"respuesta": "Proyección próximos 7 días: ...", "intent": "prediccion"}
```

---

## Flujo 4 — Chatbot cliente con bloqueo de seguridad

```
POST /api/chatbot/mensaje/
Body: {"mensaje": "cuanto han vendido este mes", "session_id": "uuid"}
User.role = "client"
    │
    ▼
views.py:enviar_mensaje()
    │  es_cliente = True → usa canal cliente
    │
    ▼
client_router.py:detectar_intencion_cliente("cuanto han vendido este mes")
    │
    ├── Evalúa todos los patterns del canal cliente:
    │    saludo, ayuda, horarios_contacto, listar_categorias,
    │    consultar_precio, verificar_disponibilidad, buscar_catalogo
    │
    ├── Ningún pattern coincide con "cuanto han vendido este mes"
    │    (el intent ventas_por_periodo NO EXISTE en client_router.py)
    │
    └── → intent = "desconocido"
    │
    ▼
client_handlers.py:ejecutar_intencion_cliente({"intent": "desconocido"})
    │  → Retorna mensaje genérico
    │  → NO consulta ninguna tabla de ventas
    │  → NO llama al LLM
    │
    ▼
HTTP 200: {
  "respuesta": "No entendí tu consulta. Puedo ayudarte con: precios, disponibilidad...",
  "intent": "desconocido"
}

RESULTADO: Datos internos no expuestos ✅
```

---

## Flujo 5 — Compra recibida → registro automático en caja

```
PATCH /api/purchases/purchases/3/
Body: {"status": "received"}
    │
    ▼
PurchaseSerializer.update()
    │
    ▼
Signal: pre_save (Purchase)
    │  old_status = "pending"
    │  new_status = "received"
    │  → cambio detectado
    │
    ▼
signal_handler:purchase_to_cash()
    │
    ├── Crea CashMovement:
    │    INSERT INTO cash_movement (
    │        type='expense',
    │        category='purchase',
    │        amount=purchase.total,
    │        date=purchase.date,
    │        description='Compra #3 — Proveedor ABC'
    │    )
    │
    ▼
HTTP 200 — Purchase actualizada + CashMovement creado automáticamente
```

---

## Flujo 6 — Sesión de caja (apertura de turno)

```
Frontend: CashView.vue monta → GET /api/cash/sessions/today/
    │
    ├── Si respuesta = 200: sesión ya abierta → mostrar info de apertura
    │
    └── Si respuesta = 404: sesión no abierta → mostrar modal "Apertura de caja"
         │
         ├── Usuario ingresa monto inicial: $200.00
         │
         ▼
        POST /api/cash/sessions/
        Body: {"opening_amount": 200.00}
         │
         ├── Crea CashSession:
         │    INSERT INTO cash_session (
         │        date=today, opened_by=user_id,
         │        opening_amount=200.00, created_at=now
         │    )
         │
         ▼
        GET /api/cash/balance/
         │
         ├── caja_final = opening_amount + ingresos - egresos
         │             = $200 + $1,245.50 - $350.00 = $1,095.50
         │
         ▼
        Frontend muestra balance completo
```

---

## Diagrama de componentes del sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vue 3)                        │
│                                                                  │
│  Pinia Store ─── Axios (401 retry) ─── Vue Router (guards)     │
│                                                                  │
│  SalesView ── InventoryView ── CashView ── ChatBot.vue          │
└───────────────────────┬─────────────────────────────────────────┘
                        │ HTTP/JSON (Bearer JWT)
┌───────────────────────▼─────────────────────────────────────────┐
│                    DJANGO 6.0.2 / DRF 3.16.1                    │
│                                                                  │
│  Middleware stack:                                               │
│  1. TenantMainMiddleware → schema_name = tenant                 │
│  2. ModuleAccessMiddleware → verifica módulos habilitados        │
│  3. JWTAuthentication → valida token                            │
│  4. IsAuthenticated / IsNotClient → permission classes          │
│                                                                  │
│  ┌──────────────┬────────────────┬──────────────────────────┐  │
│  │  ERP modules │   Chatbot      │   Predicción ML          │  │
│  │  sales/      │  router.py     │   predictor.py           │  │
│  │  inventory/  │  handlers.py   │   CatBoost V22           │  │
│  │  purchases/  │  llm_fallback  │   5 modelos .pkl         │  │
│  │  cash_mgmt/  │  (GPT-4o mini) │   metadata_v22.json      │  │
│  │  tech_svc/   │  client_*.py   │   78 features            │  │
│  └──────────────┴────────────────┴──────────────────────────┘  │
│                                                                  │
│  Signals: Venta→CashMovement | Purchase(received)→CashMovement  │
└───────────────────────┬─────────────────────────────────────────┘
                        │ django_tenants postgresql_backend
┌───────────────────────▼─────────────────────────────────────────┐
│                     PostgreSQL 14+                               │
│  schema: public          │  schema: magic_world                  │
│  ─ tenants_company       │  ─ ventas_venta / ventaitem           │
│  ─ tenants_domain        │  ─ inventory_product / category       │
│  ─ core_module           │  ─ purchases_purchase / item          │
│                          │  ─ cash_movement / cash_session       │
│                          │  ─ technical_service_ticket           │
│                          │  ─ chatbot_session / message          │
│                          │  ─ users_user                         │
└─────────────────────────────────────────────────────────────────┘
```
