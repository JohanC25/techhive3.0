# TechHive 3.0

ERP SaaS multi-tenant para pequeñas y medianas empresas. Cada empresa opera en su propio esquema PostgreSQL con módulos activables de forma independiente. Incluye chatbot conversacional con fallback LLM y predicción de ventas mediante un ensemble de modelos CatBoost (v22).

---

## Requisitos del sistema

| Herramienta | Versión mínima |
|------------|----------------|
| Python | 3.11+ |
| PostgreSQL | 14+ |
| Node.js | 18+ (recomendado 20 o 22) |
| npm | 9+ |

---

## Variables de entorno

Crear `backend/.env` copiando el siguiente ejemplo:

```dotenv
# ── Base de datos ────────────────────────────────────────────
DB_NAME=techhive_db
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
DB_HOST=localhost
DB_PORT=5432

# ── Django ───────────────────────────────────────────────────
SECRET_KEY=cambia-esto-por-una-clave-secreta-de-50-caracteres
DEBUG=True
# En producción: DEBUG=False y ALLOWED_HOSTS=tu-dominio.com

# ── Chatbot LLM (GPT-4o mini) ────────────────────────────────
OPENAI_API_KEY=sk-...

# ── Portal de administración ─────────────────────────────────
ADMIN_MASTER_KEY=clave-maestra-del-portal-admin
```

> `OPENAI_API_KEY` es opcional. Sin ella el chatbot usa únicamente el router de regex; el fallback LLM quedará desactivado.

---

## Instalación — Backend

```bash
cd backend

# 1. Entorno virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Dependencias
pip install -r requirements.txt

# 3. Variables de entorno
cp .env.example .env            # luego editar con tus valores

# 4. Crear base de datos PostgreSQL
createdb techhive_db
# o desde psql: CREATE DATABASE techhive_db;

# 5. Migraciones
python manage.py migrate_schemas --shared   # tablas del schema public
python manage.py migrate_schemas            # tablas de todos los tenants

# 6. Setup inicial
python manage.py setup_public_tenant        # crea el tenant 'public'
python manage.py seed_modules               # inserta los módulos disponibles

# 7. Crear un tenant de empresa
#    (también se puede hacer desde el portal admin en el navegador)
python manage.py shell
```

```python
# Dentro del shell de Django:
from apps.tenants.models import Company, Domain
from django.core.management import call_command
from django_tenants.utils import schema_context

company = Company(schema_name='mi_empresa', name='Mi Empresa S.A.')
company.save()                              # crea el schema en PostgreSQL

Domain.objects.create(domain='mi_empresa.localhost', tenant=company, is_primary=True)

from apps.core.models import Module
company.modules.set(Module.objects.all())  # activar todos los módulos

call_command('migrate_schemas', schema_name='mi_empresa', verbosity=1)

with schema_context('mi_empresa'):
    from apps.users.models import User
    User.objects.create_superuser('admin', '', 'password123', role='admin')
```

```bash
# 8. Modelos de predicción ML
#    Copiar los archivos .pkl y metadata_v22.json al directorio de modelos:
cp /ruta/a/modelos/*.pkl backend/apps/prediccion/ml_models/
cp /ruta/a/modelos/metadata_v22.json backend/apps/prediccion/ml_models/

#    Archivos requeridos:
#      magic_direct_v22.pkl
#      magic_ratio_v22.pkl
#      pap_direct_v22.pkl
#      pap_ratio_v22.pkl
#      global_v22.pkl
#      metadata_v22.json

# 9. Arrancar el servidor
python manage.py runserver
```

El backend quedará disponible en `http://localhost:8000`.

---

## Instalación — Frontend

```bash
cd frontend

# 1. Dependencias
npm install

# 2. Servidor de desarrollo (proxy a localhost:8000)
npm run dev
```

El frontend quedará disponible en `http://localhost:5173`.

### Configurar hosts locales

Agregar al archivo de hosts del sistema (`/etc/hosts` en Linux/Mac, `C:\Windows\System32\drivers\etc\hosts` en Windows):

```
127.0.0.1  admin.localhost
127.0.0.1  mi_empresa.localhost
```

| Portal | URL |
|--------|-----|
| Admin maestro | `http://admin.localhost:5173` |
| Tenant empresa | `http://mi_empresa.localhost:5173` |

---

## Pruebas del chatbot

El evaluador ejecuta casos de prueba automatizados contra el router de intenciones y calcula Accuracy, Macro F1 y Macro Precision.

```bash
cd backend

# Evaluar canal staff (67 casos — 14 intenciones)
python apps/chatbot/evaluar_chatbot.py --modo staff

# Evaluar canal cliente (56 casos — 7 intenciones)
python apps/chatbot/evaluar_chatbot.py --modo cliente
```

Resultados esperados (v22):

| Canal | Casos | Accuracy | Macro F1 |
|-------|-------|----------|----------|
| Staff | 67 | 100 % | 100 % |
| Cliente | 56 | 100 % | 100 % |

---

## Endpoints principales

### Autenticación

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/login/` | Obtener tokens JWT (`access` + `refresh`) |
| POST | `/api/refresh/` | Renovar `access` token |

### Módulos del ERP (requieren `Authorization: Bearer <token>`)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET/POST | `/api/users/` | Gestión de usuarios |
| GET | `/api/users/me/` | Perfil del usuario autenticado |
| GET | `/api/users/modules/` | Módulos habilitados para el tenant |
| GET/POST | `/api/sales/ventas/` | Ventas (cabecera + ítems) |
| GET/POST | `/api/inventory/products/` | Productos |
| GET | `/api/inventory/products/catalog/` | Catálogo público (accesible sin módulo) |
| GET/POST | `/api/inventory/categories/` | Categorías |
| GET/POST | `/api/inventory/shelves/` | Perchas |
| GET/POST | `/api/purchases/` | Órdenes de compra |
| GET/POST | `/api/purchases/suppliers/` | Proveedores |
| GET/POST | `/api/cash/movements/` | Movimientos de caja |
| GET | `/api/cash/movements/balance/` | Balance: monto inicial + ingresos − egresos |
| GET/POST | `/api/cash/sessions/` | Sesiones de caja (apertura de turno) |
| GET | `/api/cash/sessions/today/` | Sesión de hoy (404 si no abierta) |
| GET/POST | `/api/technical-service/tickets/` | Tickets de servicio técnico |
| GET | `/api/reports/dashboard/` | KPIs generales del negocio |
| GET | `/api/reports/ventas-por-dia/` | Ventas por día para gráficas |

### Chatbot y predicción ML

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/chatbot/mensaje/` | Enviar mensaje al chatbot |
| GET | `/api/chatbot/historial/<session_id>/` | Historial de una sesión |
| DELETE | `/api/chatbot/historial/<session_id>/limpiar/` | Borrar sesión |
| GET | `/api/chatbot/health/` | Health check |
| GET | `/api/prediccion/?dias=7` | Pronóstico de ventas (1–90 días) |

### Portal de administración (`admin.localhost`)

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/admin/login/` | Autenticación con `ADMIN_MASTER_KEY` |
| GET/POST | `/api/admin/companies/` | Listar / crear empresas (provisiona schema) |
| DELETE | `/api/admin/companies/<id>/` | Eliminar empresa |
| PUT | `/api/admin/companies/<id>/modules/` | Actualizar módulos activos |
| GET | `/api/admin/modules/` | Listar módulos disponibles |

---

## Estructura de archivos

```
techhive3.0/
├── backend/
│   ├── config/
│   │   ├── settings.py          — configuración Django (SHARED/TENANT_APPS, JWT, DB)
│   │   ├── tenant_urls.py       — rutas /api/* para tenants
│   │   └── public_urls.py       — rutas del portal admin
│   ├── apps/
│   │   ├── core/                — Module, IsNotClient, ModuleAccessMiddleware
│   │   ├── tenants/             — Company, Domain, admin CRUD
│   │   ├── users/               — User (roles), serializers con auto-username
│   │   ├── chatbot/
│   │   │   ├── router.py        — 14 intenciones staff (regex)
│   │   │   ├── handlers.py      — SQL handlers staff
│   │   │   ├── client_router.py — 7 intenciones cliente (regex)
│   │   │   ├── client_handlers.py — handlers catálogo (sin exponer costo/SKU)
│   │   │   ├── llm_fallback.py  — scope guard + GPT-4o mini
│   │   │   └── evaluar_chatbot.py — 123 casos de prueba
│   │   ├── prediccion/
│   │   │   ├── predictor.py     — TechHivePredictor singleton, forecast v22
│   │   │   └── ml_models/       — *.pkl + metadata_v22.json
│   │   └── modules/
│   │       ├── sales/           — Venta, VentaItem, signals → CashMovement
│   │       ├── inventory/       — Product, Category, Shelf
│   │       ├── purchases/       — Purchase, PurchaseItem, signal → CashMovement
│   │       ├── cash_management/ — CashSession, CashMovement
│   │       ├── technical_service/ — ServiceTicket
│   │       └── reports/         — dashboard, ventas-por-dia, compras
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── router/index.ts      — rutas tenant/admin, guards por rol
│       ├── stores/auth.ts       — JWT, fetchUser, refresh automático
│       ├── services/api.ts      — Axios con interceptor 401 → refresh
│       ├── components/
│       │   ├── AppLayout.vue    — sidebar + contenido
│       │   └── ChatBot.vue      — widget flotante del chatbot
│       └── views/               — Dashboard, Sales, Inventory, Cash, ...
├── docs/                        — documentación técnica completa
└── ModeloPrediccionVentasFinalDjango.ipynb — notebook de entrenamiento ML
```

---

## Roles de usuario

| Rol | Acceso |
|-----|--------|
| `admin` | Acceso total al ERP del tenant |
| `manager` | Igual que admin; puede gestionar usuarios |
| `employee` | Acceso a módulos habilitados |
| `client` | Solo catálogo público y chatbot de cliente |

## Módulos activables por tenant

| Código | Descripción |
|--------|-------------|
| `inventory` | Productos, categorías y perchas |
| `sales` | Registro de ventas con ítems |
| `purchases` | Compras y proveedores |
| `cash_management` | Caja, sesiones y movimientos |
| `reports` | KPIs y gráficas |
| `technical_service` | Tickets de servicio técnico |

---

## Documentación técnica

Ver la carpeta [`docs/`](./docs/README.md) para arquitectura detallada, flujos de request, seguridad, riesgos y guías de instalación extendidas.
