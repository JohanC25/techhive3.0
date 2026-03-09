# Backend — TechHive 3.0

Django 6 + Django REST Framework + django-tenants. API REST para el ERP multi-tenant.

## Stack

- **Django 6.0** con django-tenants 3.10 (esquemas PostgreSQL por empresa)
- **DRF 3.16** con SimpleJWT para autenticación
- **PostgreSQL** como única base de datos soportada
- **Anthropic SDK** (opcional) para fallback LLM en el chatbot

## Instalación

```bash
cd backend
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Variables de entorno

Crear un archivo `.env` en `backend/`:

```env
DB_NAME=techhive_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=django-insecure-cambia-esto-en-produccion

# Clave maestra para el portal admin (gestión de empresas)
ADMIN_MASTER_KEY=tu-clave-admin-segura

# Opcional: habilita fallback Claude Haiku en el chatbot
ANTHROPIC_API_KEY=sk-ant-...
```

| Variable           | Requerida | Descripción                                      |
|--------------------|-----------|--------------------------------------------------|
| `DB_NAME`          | Sí        | Nombre de la base de datos PostgreSQL            |
| `DB_USER`          | Sí        | Usuario de PostgreSQL                            |
| `DB_PASSWORD`      | Sí        | Contraseña de PostgreSQL                         |
| `DB_HOST`          | Sí        | Host de PostgreSQL                               |
| `DB_PORT`          | Sí        | Puerto de PostgreSQL (por defecto 5432)          |
| `SECRET_KEY`       | Sí        | Clave secreta de Django                          |
| `ADMIN_MASTER_KEY` | Sí        | Clave para autenticarse en el portal admin       |
| `ANTHROPIC_API_KEY`| No        | Habilita Claude Haiku como fallback del chatbot  |

## Setup inicial

```bash
# 1. Crear la base de datos en PostgreSQL
createdb techhive_db

# 2. Ejecutar migraciones del schema público (tenants, módulos)
python manage.py migrate_schemas --shared

# 3. Ejecutar migraciones en todos los schemas
python manage.py migrate_schemas

# 4. Crear el tenant público y admin por defecto
python manage.py setup_public_tenant

# 5. Cargar los módulos disponibles en la BD
python manage.py seed_modules

# 6. Iniciar servidor de desarrollo
python manage.py runserver
```

## Comandos de gestión

| Comando                                    | Descripción                                              |
|--------------------------------------------|----------------------------------------------------------|
| `migrate_schemas --shared`                 | Aplica migraciones al schema público                     |
| `migrate_schemas`                          | Aplica migraciones a todos los schemas de tenants        |
| `setup_public_tenant`                      | Crea tenant público (`localhost`) con usuario admin      |
| `seed_modules`                             | Inserta los 6 módulos disponibles en la tabla `Module`   |
| `cargar_ventas --tenant <schema>`          | Carga datos de prueba de ventas en un tenant             |

## Estructura de apps

```
apps/
├── core/           Módulos del sistema y middleware de acceso
├── tenants/        Modelos Company/Domain, vistas admin, auth admin
├── users/          CustomUser con roles (admin, staff, client)
├── chatbot/        Router regex + handlers + LLM fallback
└── modules/
    ├── inventory/          Productos y catálogo
    ├── sales/              Ventas
    ├── purchases/          Compras
    ├── cash_management/    Caja
    ├── reports/            Reportes
    └── technical_service/  Servicio técnico
```

## API Endpoints

### Portal Admin (schema público — `localhost`)

| Método | Endpoint                        | Descripción                              | Auth           |
|--------|---------------------------------|------------------------------------------|----------------|
| POST   | `/api/admin/login/`             | Obtener token admin con `ADMIN_MASTER_KEY` | Ninguna      |
| GET    | `/api/admin/modules/`           | Listar módulos disponibles               | Token admin    |
| GET    | `/api/admin/companies/`         | Listar todas las empresas                | Token admin    |
| POST   | `/api/admin/companies/`         | Crear nueva empresa (tenant)             | Token admin    |
| GET    | `/api/admin/companies/<id>/`    | Detalle de empresa                       | Token admin    |
| PUT    | `/api/admin/companies/<id>/`    | Actualizar empresa                       | Token admin    |
| DELETE | `/api/admin/companies/<id>/`    | Eliminar empresa y su schema             | Token admin    |

### Tenant (schema de empresa)

#### Autenticación

| Método | Endpoint                        | Descripción                    | Auth        |
|--------|---------------------------------|--------------------------------|-------------|
| POST   | `/api/users/login/`             | Login → access + refresh tokens | Ninguna   |
| POST   | `/api/users/token/refresh/`     | Renovar access token           | Ninguna     |
| GET    | `/api/users/me/`                | Perfil del usuario autenticado | JWT         |

#### Usuarios

| Método | Endpoint                        | Descripción                    | Auth        |
|--------|---------------------------------|--------------------------------|-------------|
| GET    | `/api/users/`                   | Listar usuarios del tenant     | JWT + admin |
| POST   | `/api/users/`                   | Crear usuario                  | JWT + admin |
| GET    | `/api/users/<id>/`              | Detalle de usuario             | JWT + admin |
| PUT    | `/api/users/<id>/`              | Actualizar usuario             | JWT + admin |
| DELETE | `/api/users/<id>/`              | Eliminar usuario               | JWT + admin |

#### Inventario

| Método | Endpoint                              | Descripción                             | Auth       |
|--------|---------------------------------------|-----------------------------------------|------------|
| GET    | `/api/inventory/products/`            | Listar productos (con paginación)       | JWT        |
| POST   | `/api/inventory/products/`            | Crear producto                          | JWT        |
| GET    | `/api/inventory/products/<id>/`       | Detalle de producto                     | JWT        |
| PUT    | `/api/inventory/products/<id>/`       | Actualizar producto                     | JWT        |
| DELETE | `/api/inventory/products/<id>/`       | Eliminar producto                       | JWT        |
| GET    | `/api/inventory/products/catalog/`    | Catálogo público (clients + staff)      | JWT        |

#### Chatbot

| Método | Endpoint                              | Descripción                             | Auth       |
|--------|---------------------------------------|-----------------------------------------|------------|
| POST   | `/api/chatbot/mensaje/`               | Enviar mensaje al chatbot               | JWT        |
| GET    | `/api/chatbot/historial/<session_id>/`| Ver historial de una sesión             | JWT        |
| DELETE | `/api/chatbot/historial/<session_id>/`| Eliminar sesión (nuevo chat)            | JWT        |
| GET    | `/api/chatbot/health/`                | Health check del chatbot                | Ninguna    |

## Multi-tenancy

- Cada empresa se identifica por su dominio (`empresa.localhost` en desarrollo)
- El middleware `TenantMainMiddleware` selecciona el schema PostgreSQL según el Host header
- El middleware `ModuleAccessMiddleware` bloquea endpoints si el módulo no está activo para ese tenant
- El endpoint `/api/inventory/products/catalog/` está exento del bloqueo de módulos para permitir acceso a clientes

## Chatbot — Arquitectura

```
Mensaje entrante
    ↓
Regex Router (gratis, <1ms)
    ├── intent detectado → Handler directo → Respuesta
    └── intent = "desconocido"
            ↓
        Claude Haiku API (si ANTHROPIC_API_KEY configurada)
            ├── Respuesta LLM → Respuesta
            └── Sin API key → Handler "desconocido" por defecto
```

- **Staff/Admin**: router en `chatbot/router.py`, handlers en `chatbot/handlers.py`
- **Cliente**: router en `chatbot/client_router.py`, handlers en `chatbot/client_handlers.py`

### Evaluar precisión del router

```bash
cd apps/chatbot

# Evaluar router de staff
python evaluar_chatbot.py --version "v1" --modo staff

# Evaluar router de clientes
python evaluar_chatbot.py --version "v1-client" --modo cliente
```
