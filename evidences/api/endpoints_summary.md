# Endpoints REST — TechHive 3.0

**Base URL:** `http://{tenant}.techhive.local:8000`
**Autenticación:** Bearer JWT en header `Authorization: Bearer <access_token>`
**Tenant activo:** determinado por el `Host` header (django-tenants)

---

## Autenticación

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| POST | `/api/token/` | No | Obtener access + refresh token |
| POST | `/api/token/refresh/` | No | Renovar access token con refresh |

---

## Usuarios

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/users/` | Sí | staff/admin | Listar usuarios del tenant |
| POST | `/api/users/` | Sí | admin | Crear usuario |
| GET | `/api/users/{id}/` | Sí | staff/admin | Detalle de usuario |
| PUT/PATCH | `/api/users/{id}/` | Sí | admin | Actualizar usuario |
| DELETE | `/api/users/{id}/` | Sí | admin | Eliminar usuario |
| POST | `/api/users/change_password/` | Sí | cualquiera | Cambiar contraseña propia |

---

## Inventario

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/inventory/products/` | Sí | staff | Listar productos |
| POST | `/api/inventory/products/` | Sí | staff | Crear producto |
| GET | `/api/inventory/products/{id}/` | Sí | staff | Detalle de producto |
| PUT/PATCH | `/api/inventory/products/{id}/` | Sí | staff | Actualizar producto |
| DELETE | `/api/inventory/products/{id}/` | Sí | staff | Eliminar producto |
| GET | `/api/inventory/categories/` | Sí | staff | Listar categorías |
| POST | `/api/inventory/categories/` | Sí | staff | Crear categoría |
| GET | `/api/inventory/shelves/` | Sí | staff | Listar perchas |
| POST | `/api/inventory/shelves/` | Sí | staff | Crear percha |

---

## Ventas

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/sales/ventas/` | Sí | staff | Listar ventas |
| POST | `/api/sales/ventas/` | Sí | staff | Crear venta (con ítems nested) |
| GET | `/api/sales/ventas/{id}/` | Sí | staff | Detalle de venta |
| PUT/PATCH | `/api/sales/ventas/{id}/` | Sí | staff | Actualizar venta |
| DELETE | `/api/sales/ventas/{id}/` | Sí | staff | Eliminar venta |

---

## Compras

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/purchases/purchases/` | Sí | staff | Listar órdenes de compra |
| POST | `/api/purchases/purchases/` | Sí | staff | Crear orden de compra |
| PATCH | `/api/purchases/purchases/{id}/` | Sí | staff | Actualizar estado (ej: received) |
| GET | `/api/purchases/suppliers/` | Sí | staff | Listar proveedores |
| POST | `/api/purchases/suppliers/` | Sí | staff | Crear proveedor |

---

## Caja (Cash Management)

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/cash/movements/` | Sí | staff | Listar movimientos de caja |
| POST | `/api/cash/movements/` | Sí | staff | Registrar movimiento manual |
| GET | `/api/cash/balance/` | Sí | staff | Balance del día (ingresos - egresos) |
| GET | `/api/cash/sessions/today/` | Sí | staff | Sesión de caja de hoy (404 si no abierta) |
| POST | `/api/cash/sessions/` | Sí | staff | Abrir sesión de caja (monto inicial) |

---

## Servicio Técnico

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/technical-service/tickets/` | Sí | staff | Listar tickets |
| POST | `/api/technical-service/tickets/` | Sí | staff | Crear ticket |
| GET | `/api/technical-service/tickets/{id}/` | Sí | staff | Detalle de ticket |
| PATCH | `/api/technical-service/tickets/{id}/` | Sí | staff | Actualizar estado/diagnóstico |

---

## Reportes

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/reports/ventas/` | Sí | staff | Reporte de ventas por período |
| GET | `/api/reports/inventario/` | Sí | staff | Reporte de inventario con alertas |
| GET | `/api/reports/caja/` | Sí | staff | Reporte de movimientos de caja |

---

## Predicción ML

| Método | Endpoint | Auth | Rol mínimo | Descripción |
|--------|----------|------|------------|-------------|
| GET | `/api/prediccion/?dias=7` | Sí | staff | Predicción de ventas (1–90 días) |

**Query params:**
- `dias` (int, default=7): horizonte de predicción (máx 90)

**Response exitosa (200):**
```json
{
  "predicciones": [
    {"fecha": "2026-04-05", "prediccion": 142.50},
    {"fecha": "2026-04-06", "prediccion": 98.30}
  ],
  "tenant": "magic_world",
  "horizonte_dias": 7
}
```

---

## Chatbot

| Método | Endpoint | Auth | Rol | Descripción |
|--------|----------|------|-----|-------------|
| POST | `/api/chatbot/mensaje/` | Sí | staff o client | Enviar mensaje al chatbot |
| GET | `/api/chatbot/sesiones/` | Sí | staff | Historial de sesiones |

**Body del request:**
```json
{
  "mensaje": "cuanto vendimos hoy",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Behavior por rol:**
- `role=staff/admin`: router de 14 intents → handlers SQL + ML → GPT-4o mini fallback
- `role=client`: router de 7 intents → handlers catálogo → GPT-4o mini fallback (acotado)

---

## Core / Tenants (URLs públicas)

| Método | Endpoint | Host | Descripción |
|--------|----------|------|-------------|
| GET | `/api/tenants/` | public | Listar empresas registradas |
| POST | `/api/tenants/` | public | Crear nueva empresa (tenant) |
| GET | `/api/core/modules/` | tenant | Módulos disponibles para el tenant |

---

## Notas de autorización

- `IsAuthenticated`: cualquier usuario con JWT válido
- `IsNotClient`: staff, admin — bloquea usuarios con `role=client`
- El tenant es determinado automáticamente por `Host` header vía `TenantMainMiddleware`
- Los tokens JWT son por-tenant: un token de `magic.techhive.local` no funciona en `papeleria.techhive.local`
