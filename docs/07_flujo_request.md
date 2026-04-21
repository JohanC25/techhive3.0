# 07 — Flujo Completo Request → Respuesta

Se documentan tres flujos representativos del sistema.

---

## Flujo A — Consulta de ventas por ERP staff

**Request**: `GET http://magic_world.localhost/api/reports/dashboard/?fecha_inicio=2025-04-01&fecha_fin=2025-04-30`

```
Browser (Vue DashboardView)
 │
 │  GET /api/reports/dashboard/?fecha_inicio=2025-04-01&fecha_fin=2025-04-30
 │  Header: Authorization: Bearer eyJ...
 │
 ▼
[1] Django WSGI / Gunicorn
 │
 ▼
[2] TenantMainMiddleware
 │   - Extrae hostname: magic_world.localhost
 │   - SELECT * FROM public.tenants_domain WHERE domain = 'magic_world.localhost'
 │   - Obtiene Company{schema_name='magic_world'}
 │   - connection.set_schema('magic_world')
 │
 ▼
[3] ModuleAccessMiddleware.process_view()
 │   - resolver.namespace = 'reports'
 │   - SELECT ... FROM tenants_company_modules WHERE company_id=X AND module.code='reports'
 │   - Módulo 'reports' habilitado → continúa
 │
 ▼
[4] SecurityMiddleware, SessionMiddleware, AuthenticationMiddleware
 │   - JWTAuthentication.authenticate(): decodifica JWT, obtiene user_id=5
 │   - SELECT * FROM magic_world.users_user WHERE id=5 → user{role='manager'}
 │
 ▼
[5] DRF dispatch → dashboard_summary(request)
 │   - permission_classes=[IsAuthenticated] → OK (es manager)
 │   - fecha_inicio='2025-04-01', fecha_fin='2025-04-30'
 │
 ▼
[6] Queries en schema magic_world:
 │   - SELECT SUM(total), COUNT(*), AVG(total) FROM ventas_venta WHERE fecha_venta BETWEEN ...
 │   - SELECT SUM(amount) FROM cash_movement WHERE type='income' AND date BETWEEN ...
 │   - SELECT COUNT(*) FROM inventory_product WHERE stock <= stock_min AND is_active=TRUE
 │   - SELECT COUNT(*) FROM technical_service_ticket WHERE status NOT IN (...)
 │
 ▼
[7] Response JSON 200
    {
      "periodo": {...},
      "ventas": {"total": 18420.50, "transacciones": 95, ...},
      "caja": {"ingresos": 18420.50, "egresos": 9100.00, "balance": 9320.50},
      "inventario": {"total_productos": 148, "productos_stock_bajo": 6},
      "servicio_tecnico": {"tickets_abiertos": 3, "tickets_completados_periodo": 14}
    }
 │
 ▼
Browser → DashboardView renderiza KPI cards y gráfica
```

---

## Flujo B — Mensaje al chatbot (staff, con predicción ML)

**Request**: `POST /api/chatbot/mensaje/` `{"mensaje": "predicción para los próximos 7 días"}`

```
Browser (ChatBot.vue)
 │
 │  POST /api/chatbot/mensaje/
 │  { "mensaje": "predicción para los próximos 7 días", "session_id": "abc-uuid" }
 │
 ▼
[1] TenantMainMiddleware → schema = magic_world
[2] ModuleAccessMiddleware → namespace='chatbot' → EXCLUIDO → continúa
[3] JWTAuthentication → user{role='employee'}
 │
 ▼
[4] enviar_mensaje(request)
 │   - mensaje = "predicción para los próximos 7 días"
 │   - len(mensaje) = 37 ≤ 500 → OK
 │   - session_id = "abc-uuid"
 │   - tenant_schema = connection.schema_name = 'magic_world'
 │   - ChatSession.get_or_create(session_id='abc-uuid')
 │   - ChatMessage.create(role='user', content='predicción...')
 │
 ▼
[5] role='employee' → router staff
 │   detectar_intencion("predicción para los próximos 7 días")
 │   - Pre-check alerta_demanda → no match
 │   - Itera INTENT_PATTERNS:
 │     - pattern 'prediccion': r'predic|pronos|forecast|proyecc' → MATCH
 │     - Extrae parámetro dias=7 del mensaje
 │   - retorna {'intent': 'prediccion', 'params': {'dias': 7}, 'confianza': 'alta'}
 │
 ▼
[6] ejecutar_intencion({'intent': 'prediccion', 'params': {'dias': 7}})
 │   → HANDLERS['prediccion'](params)
 │   → handle_prediccion(dias=7)
 │     - get_predictor() → TechHivePredictor (ya cargado en memoria)
 │     - predictor.recursive_forecast_v22(tenant='magic_world', dias=7)
 │       ├── _get_history(): SELECT fecha_venta, SUM(total) FROM ventas_venta
 │       │                   GROUP BY fecha_venta ORDER BY fecha_venta
 │       ├── Descarga clima Quito (Meteostat, cache 24h)
 │       └── Forecast día a día (78 features por fila):
 │           ├── Día 1: build_future_feature_row_v22(date=2025-04-05)
 │           │         blend(magic_direct.predict, magic_ratio.predict, global.predict)
 │           │         × seg_mult[is_weekend × is_holiday]
 │           ├── Día 2: (usa predicción día 1 como lag1)
 │           └── ...
 │     - retorna lista de {fecha, prediccion}
 │     - Formatea texto: "Predicción 7 días:\n📅 2025-04-05: $1,420.50\n..."
 │
 ▼
[7] intent != 'desconocido' → no LLM fallback
 │
 ▼
[8] ChatMessage.create(role='bot', content=respuesta, intent='prediccion')
 │
 ▼
[9] Response 200:
    {
      "respuesta": "Predicción 7 días:\n📅 2025-04-05: $1,420.50\n...",
      "intent": "prediccion",
      "session_id": "abc-uuid",
      "confianza": "alta"
    }
 │
 ▼
ChatBot.vue renderiza respuesta con markdown básico
```

---

## Flujo C — Mensaje al chatbot (cliente, con LLM fallback)

**Request**: `POST /api/chatbot/mensaje/` `{"mensaje": "qué accesorios tienen para laptops"}` (user.role='client')

```
[1-3] Middleware chain → schema activo, user{role='client'}
 │
 ▼
[4] enviar_mensaje():
 │   - role='client' → router cliente
 │   detectar_intencion_cliente("qué accesorios tienen para laptops")
 │   - Itera 7 intenciones de cliente
 │   - buscar_catalogo: r'buscar|ver|mostrar|tienen|hay' → MATCH
 │   - extraer_nombre_producto_cliente: "laptops" (limpia prefijos)
 │   - retorna {'intent': 'buscar_catalogo', 'params': {'query': 'laptops'}}
 │
 ▼ (en este ejemplo, asumamos que no encuentra resultados exactos)
[5] ejecutar_intencion_cliente({'intent': 'buscar_catalogo', ...})
 │   - query_catalogo("laptops")
 │   - Normaliza: "laptop" → busca en inventory_product por name/description
 │   - Si no encuentra → retorna "No encontré productos con ese término..."
 │   - intent = 'buscar_catalogo' (no 'desconocido')
 │
 ▼
[6] Supongamos que la query fue "¿me pueden hacer un descuento?"
 │   - detectar_intencion_cliente → 'desconocido'
 │   - is_in_domain("me pueden hacer un descuento", 'cliente')
 │     - Verifica keywords: 'descuento' ∈ DOMAIN_KEYWORDS_CLIENTE → en dominio
 │   - fallback_cliente("me pueden hacer un descuento", categorias=['Papelería', ...])
 │     - POST api.openai.com/v1/chat/completions
 │       model: gpt-4o-mini, max_tokens: 200
 │       system: "Eres el asistente de [empresa]. Solo responde sobre catálogo..."
 │     - GPT-4o mini → "Los descuentos se manejan directamente con el equipo..."
 │
 ▼
[7] ChatMessage.create(role='bot', content=llm_resp, intent='desconocido')
 │
 ▼
Response: { "respuesta": "Los descuentos se manejan...", "intent": "desconocido", ... }
```

---

## Flujo D — Creación de venta con descuento de stock

**Request**: `POST /api/sales/ventas/` `{"fecha_venta": "2025-04-04", "items": [...], "client": 5}`

```
[1-3] Middleware → schema activo, user autenticado (IsNotClient OK)
 │
 ▼
[4] VentaSerializer.create(validated_data)
 │   - Crea Venta (cabecera)
 │   - Para cada ítem en items:
 │     - VentaItem.save() → subtotal = qty × unit_price
 │     - Si item.product → Product.stock -= qty ; Product.save()
 │   - venta.recalculate_total() → SUM(subtotales)
 │   - CashMovement.create(type='income', category='sale', amount=total)
 │
 ▼
Response 201: { id, fecha_venta, total, items: [...], client: {...} }
```
