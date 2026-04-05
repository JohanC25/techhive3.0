# 04 — Backend y Endpoints API

## Configuración base

- **Base URL por tenant**: `http://<schema>.localhost:8000`
- **Autenticación**: `Authorization: Bearer <access_token>` (JWT)
- **Paginación por defecto**: 20 registros por página (`?page=N`)
- **Content-Type**: `application/json`
- **Timezone**: `America/Guayaquil`

---

## Auth

| Método | URL | Auth | Body | Descripción |
|--------|-----|------|------|-------------|
| POST | `/api/login/` | No | `{username, password}` | Obtener access + refresh tokens |
| POST | `/api/refresh/` | No | `{refresh}` | Renovar access token |

**Respuesta de login:**
```json
{
  "access":  "eyJ...",
  "refresh": "eyJ..."
}
```

---

## Usuarios (`/api/users/`)

Namespace: `users` — exento del control de módulos.

| Método | URL | Permisos | Descripción |
|--------|-----|----------|-------------|
| GET | `/api/users/` | `IsNotClient` | Listar usuarios (filtrar por `?role=client`) |
| POST | `/api/users/` | `IsAdminOrManager` | Crear usuario |
| GET | `/api/users/<id>/` | `IsNotClient` | Detalle de usuario |
| PATCH | `/api/users/<id>/` | `IsAdminOrManager` | Actualizar usuario |
| DELETE | `/api/users/<id>/` | `IsAdminOrManager` | Eliminar usuario |
| GET | `/api/users/me/` | `IsAuthenticated` | Perfil del usuario autenticado |
| PATCH | `/api/users/me/update/` | `IsAuthenticated` | Actualizar perfil propio |
| POST | `/api/users/me/change-password/` | `IsAuthenticated` | Cambiar contraseña |
| GET | `/api/users/modules/` | `IsAuthenticated` | Módulos habilitados para este tenant |

**Campos del modelo `User`:**
```
id, username, first_name, last_name, email,
role (admin/manager/employee/client),
phone, cedula
```

**Username auto-generado**: `first_name[0].lower() + last_name.lower() + cedula[-3:]` (si se proveen los tres).

---

## Ventas (`/api/sales/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET/POST | `/api/sales/ventas/` | Listar / crear ventas |
| GET/PATCH/DELETE | `/api/sales/ventas/<id>/` | Detalle / editar / eliminar |
| GET/POST | `/api/sales/items/` | Ítems de venta |

**Modelo `Venta` (cabecera):**
```
id, client (FK User, opcional),
fecha_venta, total (auto-calculado),
metodo_pago (efectivo/transferencia/deuna/tarjeta/otro),
es_feriado, es_fin_de_semana, mes, dia_semana
```

**Modelo `VentaItem` (líneas):**
```
id, venta (FK), product (FK Product, opcional),
description, quantity, unit_price,
subtotal (= quantity × unit_price, auto-calculado en save())
```

**Al crear una venta**: el serializer llama `recalculate_total()` y crea un `CashMovement(type='income', category='sale')` automáticamente.

---

## Inventario (`/api/inventory/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET/POST | `/api/inventory/products/` | Listar / crear productos |
| GET/PATCH/DELETE | `/api/inventory/products/<id>/` | CRUD producto |
| GET | `/api/inventory/products/catalog/` | Catálogo público (accesible sin módulo habilitado) |
| GET/POST | `/api/inventory/categories/` | CRUD categorías |
| GET/POST | `/api/inventory/shelves/` | CRUD perchas |

**Modelo `Product`:**
```
id, name, sku (único), description,
price, cost (privado),
stock, stock_min,
category (FK), shelf (FK Shelf, opcional),
is_active
```

**Propiedad calculada**: `low_stock = stock <= stock_min`

**Modelo `Shelf`:**
```
id, name (único), location
```

**Categorías precargadas** (migración `0003_seed_categories`): `Servicio`, `Producto`, `Reparación`.

---

## Compras (`/api/purchases/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET/POST | `/api/purchases/` | Listar / crear órdenes de compra |
| GET/PATCH/DELETE | `/api/purchases/<id>/` | CRUD orden |
| GET/POST | `/api/purchases/suppliers/` | CRUD proveedores |

**Modelo `Purchase`:**
```
id, supplier (FK), date, status (pending/received/cancelled),
total (auto-calculado), notes
```

**Signal `pre_save`** (`purchases/signals.py`): cuando `status` cambia a `'received'`, crea `CashMovement(type='expense', category='purchase', amount=purchase.total)` automáticamente.

**Modelo `PurchaseItem`:**
```
id, purchase (FK), description, quantity, unit_price,
subtotal (auto-calculado en save())
```

---

## Caja (`/api/cash/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET/POST | `/api/cash/sessions/` | CRUD sesiones de caja |
| GET | `/api/cash/sessions/today/` | Sesión de hoy (404 si no abierta) |
| GET/POST | `/api/cash/movements/` | Listar / crear movimientos |
| GET | `/api/cash/movements/balance/` | Balance: monto inicial + ingresos − egresos |

**Filtros en `/movements/`**: `?type=income|expense`, `?category=...`, `?fecha_inicio=`, `?fecha_fin=`

**Respuesta de `/balance/`:**
```json
{
  "monto_inicial": 100.00,
  "ingresos": 850.00,
  "egresos": 320.00,
  "caja_final": 630.00
}
```

**Modelo `CashSession`:**
```
id, date (único por día), opened_by (FK User),
opening_amount, closed_at (nullable), closing_amount (nullable)
```

**Categorías de movimiento**: `sale`, `purchase`, `salary`, `service`, `rent`, `utility`, `other`

---

## Servicio Técnico (`/api/technical-service/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET/POST | `/api/technical-service/tickets/` | Listar / crear tickets |
| GET/PATCH/DELETE | `/api/technical-service/tickets/<id>/` | CRUD ticket |

**Modelo `ServiceTicket`:**
```
id, client (FK User, opcional),
client_name, client_phone, client_email,
device, serial_number, accessories,
problem, diagnosis, solution,
estimated_cost, final_cost,
status (pending/in_progress/waiting_parts/completed/delivered/cancelled),
priority (low/medium/high/urgent),
received_at, promised_at, completed_at
```

---

## Reportes (`/api/reports/`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/reports/dashboard/` | KPIs: ventas, caja, inventario, tickets |
| GET | `/api/reports/ventas-por-dia/` | Ventas agrupadas por día para gráficas |
| GET | `/api/reports/compras/` | Resumen de compras por período |

**Parámetros comunes**: `?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD`

**Respuesta de `/dashboard/`:**
```json
{
  "periodo": {"inicio": "2025-01-01", "fin": "2025-01-31"},
  "ventas": {"total": 15420.00, "transacciones": 87, "promedio": 177.24},
  "caja": {"ingresos": 15420.00, "egresos": 8200.00, "balance": 7220.00},
  "inventario": {"total_productos": 142, "productos_stock_bajo": 8},
  "servicio_tecnico": {"tickets_abiertos": 5, "tickets_completados_periodo": 12}
}
```

---

## Chatbot (`/api/chatbot/`)

| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `/api/chatbot/mensaje/` | `IsAuthenticated` | Enviar mensaje |
| GET | `/api/chatbot/historial/<session_id>/` | `IsAuthenticated` | Ver historial |
| DELETE | `/api/chatbot/historial/<session_id>/limpiar/` | `IsAuthenticated` | Borrar sesión |
| GET | `/api/chatbot/health/` | No | Health check |

**Body de `/mensaje/`:**
```json
{
  "mensaje": "¿Cuánto vendimos hoy?",
  "session_id": "uuid-opcional"
}
```

**Respuesta:**
```json
{
  "respuesta": "Hoy se registraron 12 ventas por un total de $1,240.50...",
  "intent": "ventas_hoy",
  "session_id": "abc123-...",
  "confianza": "alta"
}
```

---

## Predicción ML (`/api/prediccion/`)

| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| GET | `/api/prediccion/?dias=7` | `IsAuthenticated` | Pronóstico de ventas (1−90 días) |

**Respuesta:**
```json
{
  "predicciones": [
    {"fecha": "2025-04-05", "prediccion": 1420.50},
    {"fecha": "2025-04-06", "prediccion": 890.30},
    ...
  ],
  "tenant": "magic_world",
  "horizonte_dias": 7
}
```

---

## Admin Portal (`public_urls.py` — schema `public`)

| Método | URL | Auth | Descripción |
|--------|-----|------|-------------|
| POST | `/api/admin/login/` | Master key | Obtener token admin |
| GET | `/api/admin/companies/` | No | Listar empresas |
| POST | `/api/admin/companies/` | Admin token | Crear empresa (provisiona schema) |
| DELETE | `/api/admin/companies/<id>/` | Admin token | Eliminar empresa |
| PUT | `/api/admin/companies/<id>/modules/` | Admin token | Actualizar módulos de empresa |
| GET | `/api/admin/modules/` | No | Listar módulos disponibles |
