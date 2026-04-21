# Aislamiento Multi-Tenant — TechHive 3.0

**Mecanismo:** django-tenants 3.10 — schema-per-tenant PostgreSQL
**Garantía:** Los datos de un tenant son físicamente inaccesibles desde otro tenant

---

## ¿Cómo funciona el aislamiento?

### 1. Detección de tenant por dominio

```python
# django-tenants: TenantMainMiddleware
# Al recibir cada request:
domain = request.get_host()  # "magic.techhive.local"

company = Company.objects.get(domain__domain=domain)  # schema_name="magic_world"
connection.set_schema(company.schema_name)             # connection.schema = "magic_world"
request.tenant = company
```

### 2. Estructura en PostgreSQL

```sql
-- Consultar schemas disponibles
SELECT schema_name FROM information_schema.schemata
WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');

-- Resultado:
-- public           ← datos compartidos (tenants, dominios, módulos)
-- magic_world      ← datos exclusivos de Magic World
-- papeleria        ← datos exclusivos de Papelería Alfa & Omega
```

### 3. Separación SHARED_APPS vs TENANT_APPS

```python
# config/settings.py
SHARED_APPS = [
    'django_tenants',
    'apps.tenants',    # Company, Domain — tabla en schema 'public'
    'apps.core',       # Module — tabla en schema 'public'
]

TENANT_APPS = [
    'apps.users',                    # users_user  ← por tenant
    'apps.modules.sales',            # ventas_venta ← por tenant
    'apps.modules.inventory',        # inventory_product ← por tenant
    'apps.modules.purchases',        # purchases_purchase ← por tenant
    'apps.modules.cash_management',  # cash_movement ← por tenant
    'apps.modules.technical_service',# technical_service_ticket ← por tenant
    'apps.chatbot',                  # chatbot_session ← por tenant
    # prediccion no tiene modelos en BD (usa PKLs compartidos)
]
```

---

## Prueba de aislamiento — verificación técnica

### Escenario: Usuario de Magic World intenta acceder a datos de Papelería

```
Request: GET /api/inventory/products/
Headers:
  Host: magic.techhive.local           ← tenant resuelto por dominio
  Authorization: Bearer <token>        ← token generado en magic.techhive.local
```

**Paso 1:** `TenantMainMiddleware` resuelve `magic.techhive.local` → `schema_name="magic_world"`

**Paso 2:** `connection.set_schema("magic_world")` — todas las queries usan `magic_world.*`

**Paso 3:** Query ORM ejecutada:
```sql
-- Django ORM genera:
SELECT * FROM inventory_product WHERE is_active = TRUE;
-- Pero con schema activo "magic_world", en realidad ejecuta:
SELECT * FROM magic_world.inventory_product WHERE is_active = TRUE;
-- magic_world.inventory_product SOLO contiene productos de Magic World
```

**Resultado:** El usuario de Magic World **nunca puede ver** `papeleria.inventory_product`.

### ¿Qué pasa si se intenta un token de otro tenant?

Los tokens JWT no contienen el schema directamente, pero:
- El token es generado en el contexto del tenant activo
- Si se usa un token de Papelería en `Host: magic.techhive.local`:
  - `TenantMainMiddleware` setea schema = "magic_world"
  - El `user_id` del token (de Papelería) no existe en `magic_world.users_user`
  - → HTTP 401 Unauthorized

---

## Configuración de dominios

```
Tabla: public.tenants_domain

id | domain                    | is_primary | tenant_id
---|---------------------------|------------|----------
 1 | magic.techhive.local      | true       | 1
 2 | papeleria.techhive.local  | true       | 2
```

```
Tabla: public.tenants_company (Company)

id | name                      | schema_name  | on_trial | paid_until
---|---------------------------|--------------|----------|----------
 1 | Magic World               | magic_world  | false    | NULL
 2 | Papelería Alfa & Omega    | papeleria    | false    | NULL
```

---

## Módulos activables por tenant

```
Tabla: public.core_module

id | name              | slug           | is_enabled_default
---|-------------------|----------------|-------------------
 1 | Ventas            | sales          | true
 2 | Inventario        | inventory      | true
 3 | Compras           | purchases      | true
 4 | Caja              | cash_management| true
 5 | Servicio Técnico  | technical_service | false
 6 | Predicción ML     | prediccion     | true
 7 | Chatbot           | chatbot        | true
```

`ModuleAccessMiddleware` verifica que el módulo esté habilitado para el tenant antes de pasar el request a la view.

---

## Aislamiento del chatbot

El chatbot tiene aislamiento adicional:

```python
# handlers.py — cada handler opera en el schema del tenant activo
def handle_ventas_hoy():
    with connection.cursor() as cursor:
        # connection.schema_name ya está seteado por TenantMainMiddleware
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(total), 0)
            FROM ventas_venta
            WHERE fecha_venta = %s
        """, [date.today()])
        # Equivalente a: FROM magic_world.ventas_venta (si tenant es Magic World)
```

**Garantía:** Un handler del chatbot de Magic World nunca puede ver las ventas de Papelería porque:
1. `connection.schema_name` = "magic_world" está fijo para todo el request
2. La tabla `ventas_venta` referenciada es `magic_world.ventas_venta`
3. No hay joins entre schemas en ningún handler

---

## Resumen de garantías de aislamiento

| Nivel | Mecanismo | Garantía |
|-------|-----------|---------|
| **Base de datos** | Schema-per-tenant en PostgreSQL | `magic_world.*` y `papeleria.*` son tablas físicamente separadas |
| **ORM Django** | `connection.set_schema()` automático | Todas las queries ORM van al schema del tenant activo |
| **Middleware** | `TenantMainMiddleware` en cada request | El schema se setea ANTES de llegar a la view |
| **Autenticación** | JWT + user_id en schema del tenant | Token de un tenant no autentica en otro |
| **Módulos** | `ModuleAccessMiddleware` | Cada tenant solo accede a sus módulos habilitados |
| **Chatbot cliente** | Router y handlers separados | El canal cliente no tiene acceso a ningún dato de ventas/predicción |
