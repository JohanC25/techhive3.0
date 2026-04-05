# 02 — Arquitectura Multi-Tenant

## Estrategia: Schema-per-Tenant (PostgreSQL)

TechHive 3.0 usa **django-tenants 3.10** con la estrategia *schema-per-tenant*: cada empresa tiene su propio esquema de PostgreSQL. Esto provee aislamiento de datos a nivel de motor de base de datos, sin necesidad de lógica de filtrado en la aplicación.

```
PostgreSQL (base de datos única: techhive_db)
├── schema: public              ← datos globales compartidos
│   ├── tenants_company         ← tabla maestra de empresas
│   ├── tenants_domain          ← dominios HTTP por empresa
│   └── core_module             ← catálogo de módulos disponibles
│
├── schema: magic_world         ← empresa 1 (Magic World)
│   ├── users_user
│   ├── ventas_venta
│   ├── ventas_ventaitem
│   ├── inventory_product
│   ├── inventory_category
│   ├── inventory_shelf
│   ├── purchases_purchase
│   ├── purchases_purchaseitem
│   ├── purchases_supplier
│   ├── cash_movement
│   ├── cash_session
│   ├── technical_service_ticket
│   ├── chatbot_session
│   └── chatbot_message
│
└── schema: papeleria            ← empresa 2 (Papelería)
    └── (mismas tablas)
```

## Modelo de datos core

### `Company` (`apps/tenants/models.py`)

```python
class Company(TenantMixin):
    name        = CharField(max_length=255)
    paid_until  = DateField(null=True)
    on_trial    = BooleanField(default=True)
    modules     = ManyToManyField("core.Module")  # módulos habilitados
    auto_create_schema = True                      # crea schema automáticamente
```

- Hereda de `TenantMixin` de django-tenants.
- `auto_create_schema = True`: al llamar `company.save()`, django-tenants crea el schema PostgreSQL y ejecuta `migrate_schemas`.
- Relación M2M con `Module` para control de acceso por módulo.

### `Domain` (`apps/tenants/models.py`)

```python
class Domain(DomainMixin):
    pass  # hereda: domain (FQDN), tenant FK, is_primary
```

El dominio HTTP (`empresa.localhost`) es la clave de resolución del tenant.

### `Module` (`apps/core/models.py`)

```python
class Module(models.Model):
    code = CharField(max_length=50, unique=True)  # ej: 'sales', 'inventory'
    name = CharField(max_length=100)
```

## Resolución del tenant por request

```
Request HTTP: GET http://magic_world.localhost/api/sales/
       │
       ▼
TenantMainMiddleware
  └── busca Domain con domain='magic_world.localhost'
  └── obtiene Company con schema_name='magic_world'
  └── django.db.connection.set_schema('magic_world')
       │
       ▼
Toda la ORM → opera en schema 'magic_world'
```

El middleware es el **primer** eslabón en `MIDDLEWARE` (settings.py línea 81):

```python
MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',  # ← primero
    "apps.core.middleware.ModuleAccessMiddleware",
    ...
]
```

## Configuración en settings.py

```python
SHARED_APPS = (
    'django_tenants',
    'apps.tenants',   # Company, Domain
    'apps.core',      # Module
    'django.contrib.contenttypes',
)

TENANT_APPS = (
    'django.contrib.auth',
    'apps.users',
    'apps.modules.sales',
    'apps.modules.inventory',
    'apps.modules.purchases',
    'apps.modules.cash_management',
    'apps.modules.technical_service',
    'apps.modules.reports',
    'apps.chatbot.apps.ChatbotConfig',
    'apps.prediccion',
)

TENANT_MODEL        = "tenants.Company"
TENANT_DOMAIN_MODEL = "tenants.Domain"
DATABASE_ROUTERS    = ('django_tenants.routers.TenantSyncRouter',)
```

- Las `SHARED_APPS` tienen tablas solo en `public`.
- Las `TENANT_APPS` tienen tablas replicadas en cada schema de empresa.

## Control de módulos por tenant (`ModuleAccessMiddleware`)

```python
# apps/core/middleware.py
def process_view(self, request, view_func, view_args, view_kwargs):
    module_code = resolver.namespace  # ej: 'sales', 'inventory'
    EXCLUDED = {"users", "chatbot"}   # siempre accesibles

    if not request.tenant.modules.filter(code=module_code).exists():
        return JsonResponse({"detail": "módulo no habilitado"}, status=403)
```

Esto permite activar/desactivar módulos por tenant desde el panel de administración sin tocar código.

## Creación de un nuevo tenant (flujo)

1. Admin portal llama `POST /api/admin/companies/` con `name`, `schema_name`, `domain`, `admin_username`, `admin_password`, `modules[]`
2. `CompanyListView.post()` en `apps/tenants/views.py`:
   - Crea `Company` → django-tenants genera el schema PostgreSQL
   - Crea `Domain` con `is_primary=True`
   - Asigna módulos con `company.modules.set(modules)`
   - Ejecuta `call_command("migrate_schemas", schema_name=schema_name)`
   - Dentro de `schema_context(schema_name)`: crea usuario admin con `create_superuser`

## Portal de administración maestro

El portal admin (`admin.localhost`) usa autenticación por **clave maestra** (`ADMIN_MASTER_KEY` en `.env`) en lugar de JWT, para no requerir un tenant específico. El token admin es un JWT firmado con esa clave, decodificado por el decorador `@admin_required` en `apps/tenants/admin_auth.py`.

## Aislamiento del chatbot por tenant

El chatbot detecta el schema activo en cada request:

```python
# apps/chatbot/views.py
from django.db import connection
tenant_schema = connection.schema_name  # 'magic_world', 'papeleria', etc.
```

El `ChatSession` almacena `tenant_schema` para que el historial quede vinculado al contexto correcto.

Los SQL handlers ejecutan queries directamente sobre el schema activo (sin prefijo de schema), aprovechando que `connection.set_schema()` ya fue llamado por el middleware.
