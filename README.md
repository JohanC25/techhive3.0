# TechHive 3.0

## 1. Descripción del problema y solución

**Problema**: Las pequeñas y medianas empresas (PyMES) ecuatorianas carecen de herramientas integradas de gestión que combinen un ERP adaptable, análisis predictivo de ventas e interacción conversacional. Las soluciones existentes son costosas, monolíticas y no se adaptan a la variabilidad climática y de demanda local.

**Solución**: TechHive 3.0 es un sistema ERP SaaS multi-tenant construido sobre Django y Vue 3, donde cada empresa opera en su propio esquema PostgreSQL aislado. El sistema integra tres capacidades:

1. **ERP modular**: ventas, inventario, compras, caja, servicio técnico y reportes, con módulos activables por empresa.
2. **Predicción de ventas ML**: ensemble de tres modelos CatBoostRegressor (v22) con 78 variables de entrada que incluyen datos climáticos de Quito, feriados ecuatorianos y patrones históricos. Métricas reales en producción: MAPE 16.12 % (Magic World) y 14.87 % (Papelería Alfa & Omega).
3. **Chatbot inteligente**: arquitectura de tres capas (router regex → handlers SQL → fallback GPT-4o mini) con canales diferenciados para staff interno y clientes externos. 127 casos de prueba (67 staff + 60 cliente), precisión y F1 del 100 %.

---

## 2. Arquitectura general

```
┌─────────────────────────────────────────────────────────────┐
│  NAVEGADOR                                                   │
│  Vue 3.5 + Vite 7 + TypeScript 5.9 + Pinia 3 + Axios 1.13  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON  (Bearer JWT)
┌────────────────────────▼────────────────────────────────────┐
│  DJANGO 6.0.2 / DRF 3.16.1                                  │
│                                                              │
│  TenantMainMiddleware  →  detecta empresa por Host header    │
│  ModuleAccessMiddleware → bloquea módulos no habilitados     │
│  JWTAuthentication     → valida Bearer token                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  ERP modules │  │   Chatbot    │  │  Predicción ML   │  │
│  │  sales       │  │  router.py   │  │  predictor.py    │  │
│  │  inventory   │  │  handlers.py │  │  CatBoost v22    │  │
│  │  purchases   │  │  llm_fallback│  │  78 features     │  │
│  │  cash_mgmt   │  │  GPT-4o mini │  │  Meteostat       │  │
│  │  tech_service│  │              │  │                  │  │
│  │  reports     │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ django_tenants.postgresql_backend
┌────────────────────────▼────────────────────────────────────┐
│  PostgreSQL 14+                                              │
│  schema: public       │  schema: magic_world                 │
│  ─ tenants_company    │  ─ users_user                        │
│  ─ tenants_domain     │  ─ ventas_venta / ventas_ventaitem   │
│  ─ core_module        │  ─ inventory_product / _category     │
│                       │  ─ purchases_purchase / _supplier    │
│                       │  ─ cash_movement / cash_session      │
│                       │  ─ technical_service_ticket          │
│                       │  ─ chatbot_session / chatbot_message │
└─────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Servicios externos                                          │
│  OpenAI API (gpt-4o-mini)  │  Meteostat (clima Quito)        │
└─────────────────────────────────────────────────────────────┘
```

**Multi-tenancy**: el host HTTP (`empresa.localhost`) determina el schema PostgreSQL activo. Django-tenants conmuta el schema con `connection.set_schema()` antes de cualquier query, garantizando aislamiento de datos a nivel de motor.

---

## 3. Requisitos técnicos — versiones exactas

### Sistema operativo

Compatible con Linux, macOS y Windows 10/11. Los comandos de este documento usan shell Unix. En Windows usar Git Bash, WSL2 o PowerShell con ajuste de rutas.

### Software base

| Herramienta | Versión requerida | Verificar |
|------------|-------------------|-----------|
| Python | **3.11 o superior** | `python --version` |
| PostgreSQL | **14 o superior** | `psql --version` |
| Node.js | **20.19+ o 22.12+** | `node --version` |
| npm | **9 o superior** | `npm --version` |
| Git | cualquier versión reciente | `git --version` |

### Dependencias Python (versiones fijadas)

```
Django==6.0.2
djangorestframework==3.16.1
django-tenants==3.10.0
djangorestframework_simplejwt==5.5.1
psycopg2-binary==2.9.11
PyJWT==2.11.0
python-dateutil==2.9.0.post0
python-dotenv==1.2.1
asgiref==3.11.1
sqlparse==0.5.5
tzdata==2025.3
six==1.17.0
catboost>=1.2
joblib>=1.2
meteostat>=1.6
holidays>=0.46
numpy>=1.24
pandas>=2.0
scipy>=1.10
openai>=1.0
anthropic>=0.40.0
plotly>=5.0
```

### Dependencias Node.js (versiones mínimas)

```
vue@^3.5.28
vue-router@^5.0.3
pinia@^3.0.4
axios@^1.13.5
vite@^7.3.1
typescript@~5.9.3
```

---

## 4. Instalación paso a paso

### 4.1 Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd techhive3.0
```

### 4.2 Crear la base de datos PostgreSQL

```bash
# Conectarse a PostgreSQL como superusuario
psql -U postgres

# Dentro de psql:
CREATE DATABASE techhive_db;
\q
```

### 4.3 Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows CMD
# source venv/Scripts/activate    # Windows Git Bash

# Instalar dependencias
# NOTA: catboost es un paquete pesado (~500 MB), la primera instalación tarda 5-10 min
pip install -r requirements.txt
```

### 4.4 Frontend

```bash
# En otra terminal, desde la raíz del proyecto
cd frontend
npm install
```

---

## 5. Configuración de entorno

### 5.1 Crear el archivo .env

```bash
# Desde la carpeta backend/
cp .env.example .env   # si existe .env.example
# o crear manualmente:
touch .env
```

### 5.2 Contenido completo del .env

```dotenv
# ── Base de datos ─────────────────────────────────────────────────────
DB_NAME=techhive_db
DB_USER=postgres
DB_PASSWORD=tu_password_de_postgres
DB_HOST=localhost
DB_PORT=5432

# ── Django ────────────────────────────────────────────────────────────
# Generar con: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=cambia-esto-por-una-clave-aleatoria-de-50-caracteres-minimo

DEBUG=True
# En producción cambiar a: DEBUG=False

# ── Chatbot LLM — GPT-4o mini (fallback) ─────────────────────────────
# OPCIONAL: sin esta clave el chatbot funciona con el router de regex
# El fallback LLM queda desactivado si no se proporciona
OPENAI_API_KEY=sk-...

# ── Portal de administración maestro ─────────────────────────────────
ADMIN_MASTER_KEY=define-aqui-una-clave-segura-para-el-portal-admin

# ── Anthropic (alternativa opcional a OpenAI) ─────────────────────────
# ANTHROPIC_API_KEY=sk-ant-...
```

| Variable | ¿Requerida? | Descripción |
|----------|------------|-------------|
| `DB_NAME` | **Sí** | Nombre de la base de datos PostgreSQL |
| `DB_USER` | **Sí** | Usuario de PostgreSQL |
| `DB_PASSWORD` | **Sí** | Contraseña de PostgreSQL |
| `DB_HOST` | **Sí** | Host (generalmente `localhost`) |
| `DB_PORT` | **Sí** | Puerto PostgreSQL (por defecto `5432`) |
| `SECRET_KEY` | **Sí** | Clave secreta de Django, mínimo 50 caracteres |
| `ADMIN_MASTER_KEY` | **Sí** | Clave para el portal de gestión de empresas |
| `OPENAI_API_KEY` | No | Habilita GPT-4o mini como fallback del chatbot |
| `ANTHROPIC_API_KEY` | No | Alternativa: Claude como fallback del chatbot |

### 5.3 Configurar hosts locales

Editar el archivo de hosts del sistema operativo:

- **Linux / macOS**: `/etc/hosts`
- **Windows**: `C:\Windows\System32\drivers\etc\hosts`

Agregar las siguientes líneas:

```
127.0.0.1  admin.localhost
127.0.0.1  magic_world.localhost
127.0.0.1  papeleria.localhost
127.0.0.1  demo.localhost
```

---

## 6. Ejecución del backend

### 6.1 Setup inicial de base de datos (solo la primera vez)

```bash
cd backend
source venv/bin/activate    # si no está activo

# Paso 1: Tablas del schema público (tenants, módulos)
python manage.py migrate_schemas --shared

# Paso 2: Tablas de todos los schemas de tenants
python manage.py migrate_schemas

# Paso 3: Crear el tenant público requerido por django-tenants
python manage.py setup_public_tenant

# Paso 4: Cargar los 6 módulos disponibles en la BD
python manage.py seed_modules
```

### 6.2 Crear una empresa de prueba

```bash
python manage.py shell
```

Dentro del shell de Django:

```python
from apps.tenants.models import Company, Domain
from django.core.management import call_command
from django_tenants.utils import schema_context
from apps.core.models import Module

# Crear empresa
company = Company(schema_name='demo', name='Demo Empresa')
company.save()  # crea el schema PostgreSQL automáticamente

# Asignar dominio
Domain.objects.create(domain='demo.localhost', tenant=company, is_primary=True)

# Habilitar todos los módulos
company.modules.set(Module.objects.all())

# Migrar el schema recién creado
call_command('migrate_schemas', schema_name='demo', verbosity=1)

# Crear usuario administrador en el tenant
with schema_context('demo'):
    from apps.users.models import User
    User.objects.create_superuser('admin', '', 'admin1234', role='admin')

exit()
```

### 6.3 Copiar modelos de predicción ML

Los archivos `.pkl` y `metadata_v22.json` deben estar en `backend/apps/prediccion/ml_models/`.

```bash
ls backend/apps/prediccion/ml_models/
# Deben existir los siguientes 6 archivos:
# global_model_v22.pkl
# magic_direct_v22.pkl
# magic_ratio_v22.pkl
# metadata_v22.json
# pap_direct_v22.pkl
# pap_ratio_v22.pkl
```

Si se entrenaron con el notebook, exportarlos desde Google Drive y copiarlos:

```bash
cp /ruta/a/exportados/*.pkl backend/apps/prediccion/ml_models/
cp /ruta/a/exportados/metadata_v22.json backend/apps/prediccion/ml_models/
```

### 6.4 Arrancar el servidor

```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

El backend estará disponible en `http://localhost:8000`.

Al iniciar, el servidor lanza automáticamente en un thread daemon la carga de los modelos CatBoost (`PrediccionConfig.ready()`). El primer request de predicción puede tardar 3-8 segundos si el warmup no terminó; los siguientes son inmediatos.

---

## 7. Ejecución del frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en `http://localhost:5173`.

### Acceder a los portales

| Portal | URL | Credenciales |
|--------|-----|--------------|
| Admin maestro | `http://admin.localhost:5173` | `ADMIN_MASTER_KEY` del `.env` |
| Tenant demo | `http://demo.localhost:5173` | usuario: `admin` / contraseña: `admin1234` |

> **Importante**: el host de la URL determina el tenant activo. Asegurarse de haber configurado el archivo de hosts (sección 5.3) antes de abrir estas URLs.

---

## 8. Ejecución del modelo de predicción

### 8.1 Desde el endpoint REST

Una vez autenticado con JWT:

```bash
curl -X GET "http://demo.localhost:8000/api/prediccion/?dias=7" \
  -H "Authorization: Bearer <access_token>"
```

### 8.2 Notebooks de desarrollo

Los notebooks están en `notebooks/`:

| Notebook | Propósito |
|----------|-----------|
| `ModeloPrediccionVentasFinalDjango.ipynb` | Pipeline de producción V22. Genera los `.pkl` y `metadata_v22.json`. **Valores oficiales**: RMSE Magic = 55.47, RMSE Pap = 10.25 |
| `MejorasModeloPrediccionVentasA.ipynb` | Historial iterativo v1→v22. Muestra la evolución del modelo a lo largo de 22 versiones. Los valores de V22 en este notebook pueden diferir del anterior porque ejecuta el modelo dentro del flujo acumulado |

Para ejecutar los notebooks en Google Colab:

1. Subir `notebooks/*.ipynb` a Google Drive
2. Subir los CSV de ventas: `BD_Ventas_Magic.csv` y `BD_Ventas_Papeleria.csv`
3. Abrir el notebook con Google Colab y ejecutar celda a celda

### 8.3 Métricas del modelo en producción (metadata_v22.json)

| Tenant | RMSE | MAE | MAPE | Acc MAPE | Acc ±20% |
|--------|------|-----|------|----------|---------|
| Magic World | 55.47 | 13.86 | 16.12 % | 83.88 % | 80.00 % |
| Papelería Alfa & Omega | 10.25 | 7.87 | 14.87 % | 85.13 % | 76.47 % |

### 8.4 Pesos del ensemble (blend optimizado por cuadrícula)

| Tenant | pred_direct | pred_ratio | pred_global |
|--------|-------------|-----------|-------------|
| Magic World | 0.0 | **1.0** | 0.0 |
| Papelería | 0.0 | 0.0 | **1.0** |

---

## 9. Uso del endpoint /api/chatbot/mensaje/

### Autenticación previa (obtener JWT)

```bash
curl -X POST "http://demo.localhost:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin1234"}'
```

Respuesta:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Guardar el `access` token para los siguientes requests.

### Enviar mensaje al chatbot

**URL**: `POST /api/chatbot/mensaje/`

**Headers requeridos**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body**:
```json
{
  "mensaje": "texto del mensaje (máx. 500 caracteres)",
  "session_id": "uuid-opcional-para-mantener-historial"
}
```

- `mensaje` (requerido): texto enviado por el usuario.
- `session_id` (opcional): UUID que identifica la sesión de conversación. Si se omite, se genera uno nuevo automáticamente y se devuelve en la respuesta.

**Comportamiento según rol del usuario**:
- `role = admin / manager / employee` → canal **staff** (14 intenciones, acceso a datos del ERP)
- `role = client` → canal **cliente** (7 intenciones, solo catálogo público)

---

## 10. Ejemplos reales de request / response

### Ejemplo A — Consulta de ventas (canal staff)

```bash
curl -X POST "http://demo.localhost:8000/api/chatbot/mensaje/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "cuánto vendimos hoy",
    "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  }'
```

```json
{
  "respuesta": "📅 Ventas de hoy (2025-04-04):\n💰 Total: $1,240.50\n📦 Transacciones: 12\n💳 Promedio por venta: $103.38",
  "intent": "ventas_hoy",
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "confianza": "alta"
}
```

### Ejemplo B — Predicción ML (canal staff)

```bash
curl -X POST "http://demo.localhost:8000/api/chatbot/mensaje/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "predicción para los próximos 7 días"}'
```

```json
{
  "respuesta": "📈 Predicción de ventas — próximos 7 días:\n📅 2025-04-05: $1,380.20\n📅 2025-04-06: $920.50\n📅 2025-04-07: $1,105.80\n📅 2025-04-08: $1,420.30\n📅 2025-04-09: $980.10\n📅 2025-04-10: $1,890.60\n📅 2025-04-11: $1,450.40",
  "intent": "prediccion",
  "session_id": "a1b2c3d4-...",
  "confianza": "alta"
}
```

### Ejemplo C — Búsqueda en catálogo (canal cliente)

```bash
curl -X POST "http://demo.localhost:8000/api/chatbot/mensaje/" \
  -H "Authorization: Bearer <access_token_de_usuario_client>" \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "tienen cuadernos universitarios"}'
```

```json
{
  "respuesta": "📦 Encontré 3 producto(s) para \"cuaderno\":\n\n1. **Cuaderno Universitario 100h** — $2.50 ✅ Disponible\n2. **Cuaderno Universitario Espiral** — $3.20 ✅ Disponible\n3. **Cuaderno Universitario Pasta Dura** — $4.50 ❌ Sin stock",
  "intent": "buscar_catalogo",
  "session_id": "b2c3d4e5-...",
  "confianza": "alta"
}
```

### Ejemplo D — Predicción directa por endpoint REST

```bash
curl -X GET "http://demo.localhost:8000/api/prediccion/?dias=3" \
  -H "Authorization: Bearer <access_token>"
```

```json
{
  "predicciones": [
    {"fecha": "2025-04-05", "prediccion": 1380.20},
    {"fecha": "2025-04-06", "prediccion": 920.50},
    {"fecha": "2025-04-07", "prediccion": 1105.80}
  ],
  "tenant": "demo",
  "horizonte_dias": 3
}
```

### Ejemplo E — Historial de sesión

```bash
curl -X GET "http://demo.localhost:8000/api/chatbot/historial/f47ac10b-58cc-4372-a567-0e02b2c3d479/" \
  -H "Authorization: Bearer <access_token>"
```

```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "mensajes": [
    {"role": "user",  "content": "cuánto vendimos hoy",   "intent": null,        "created_at": "2025-04-04T15:30:00Z"},
    {"role": "bot",   "content": "📅 Ventas de hoy...",   "intent": "ventas_hoy","created_at": "2025-04-04T15:30:01Z"}
  ]
}
```

---

## 11. Estructura del proyecto

```
techhive3.0/
│
├── README.md                           ← este archivo
│
├── notebooks/
│   ├── ModeloPrediccionVentasFinalDjango.ipynb   ← pipeline producción V22
│   └── MejorasModeloPrediccionVentasA.ipynb      ← evolución iterativa v1→v22
│
├── docs/                               ← documentación técnica ampliada (12 docs)
│   ├── README.md                       ← índice
│   ├── 00_resumen.md
│   ├── 01_arquitectura_general.md
│   ├── 02_multitenancy.md
│   ├── 03_chatbot.md
│   ├── 04_api_endpoints.md
│   ├── 05_frontend.md
│   ├── 06_seguridad.md
│   ├── 07_flujo_request.md
│   ├── 08_estructura_carpetas.md
│   ├── 09_instalacion.md
│   ├── 10_dependencias.md
│   ├── 11_riesgos.md
│   └── 12_vacios_documentacion.md
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt                ← dependencias Python con versiones
│   ├── .env                            ← NO en git — variables de entorno
│   │
│   ├── config/
│   │   ├── settings.py                 ← configuración Django (SHARED/TENANT_APPS, JWT, DB)
│   │   ├── tenant_urls.py              ← rutas /api/* para tenants (ROOT_URLCONF)
│   │   ├── public_urls.py              ← rutas portal admin (PUBLIC_SCHEMA_URLCONF)
│   │   └── wsgi.py
│   │
│   ├── apps/
│   │   ├── core/
│   │   │   ├── models.py               ← Module (catálogo de módulos activables)
│   │   │   ├── permissions.py          ← IsNotClient (bloquea rol client en ERP)
│   │   │   ├── middleware.py           ← ModuleAccessMiddleware
│   │   │   └── management/commands/
│   │   │       ├── setup_public_tenant.py
│   │   │       ├── seed_modules.py
│   │   │       └── seed_demo.py
│   │   │
│   │   ├── tenants/
│   │   │   ├── models.py               ← Company (TenantMixin), Domain (DomainMixin)
│   │   │   ├── views.py                ← CRUD admin de empresas
│   │   │   └── admin_auth.py           ← autenticación por ADMIN_MASTER_KEY
│   │   │
│   │   ├── users/
│   │   │   ├── models.py               ← User (AbstractUser + role, phone, cedula)
│   │   │   ├── serializers.py          ← UserCreateSerializer (auto-username por cédula)
│   │   │   └── views.py                ← UserViewSet (me, modules, change-password)
│   │   │
│   │   ├── chatbot/
│   │   │   ├── models.py               ← ChatSession, ChatMessage
│   │   │   ├── views.py                ← enviar_mensaje() — endpoint principal
│   │   │   ├── router.py               ← 14 intenciones staff (regex INTENT_PATTERNS)
│   │   │   ├── handlers.py             ← SQL handlers staff + llamadas ML
│   │   │   ├── client_router.py        ← 7 intenciones cliente
│   │   │   ├── client_handlers.py      ← catálogo sin exponer costo/SKU/stock exacto
│   │   │   ├── llm_fallback.py         ← scope guard + GPT-4o mini
│   │   │   └── evaluar_chatbot.py      ← 127 casos de prueba automatizados (67 staff + 60 cliente)
│   │   │
│   │   ├── prediccion/
│   │   │   ├── predictor.py            ← TechHivePredictor singleton, forecast v22
│   │   │   ├── views.py                ← PrediccionView GET ?dias=N
│   │   │   ├── apps.py                 ← warmup ML en thread daemon al arrancar
│   │   │   └── ml_models/
│   │   │       ├── magic_direct_v22.pkl
│   │   │       ├── magic_ratio_v22.pkl
│   │   │       ├── pap_direct_v22.pkl
│   │   │       ├── pap_ratio_v22.pkl
│   │   │       ├── global_model_v22.pkl
│   │   │       └── metadata_v22.json
│   │   │
│   │   └── modules/
│   │       ├── sales/                  ← Venta, VentaItem → CashMovement automático
│   │       ├── inventory/              ← Product, Category, Shelf
│   │       ├── purchases/              ← Purchase, PurchaseItem + signal → CashMovement
│   │       ├── cash_management/        ← CashSession (apertura turno), CashMovement
│   │       ├── technical_service/      ← ServiceTicket (6 estados, 4 prioridades)
│   │       └── reports/                ← dashboard, ventas-por-dia, compras
│   │
│   ├── scripts/                        ← utilidades de desarrollo
│   │   ├── check_data.py
│   │   ├── fix_magic_world.py
│   │   ├── fix_migrations.py
│   │   └── load_magic_csv.py
│   │
│   └── data/
│       └── BD_Ventas_Magic.csv         ← datos históricos Magic World
│
└── frontend/
    ├── package.json
    ├── vite.config.ts                  ← proxy /api → localhost:8000
    └── src/
        ├── main.ts                     ← entry point (Pinia + Router)
        ├── router/index.ts             ← rutas tenant/admin, guards por rol
        ├── stores/
        │   ├── auth.ts                 ← JWT en localStorage, refresh automático
        │   ├── adminStore.ts           ← sesión portal admin
        │   └── toast.ts                ← notificaciones
        ├── services/
        │   ├── api.ts                  ← Axios con interceptor JWT + retry en 401
        │   └── adminApi.ts             ← Axios para portal admin
        ├── components/
        │   ├── AppLayout.vue           ← sidebar + contenido
        │   └── ChatBot.vue             ← widget flotante chatbot
        └── views/
            ├── DashboardView.vue       ← KPIs + gráfica de ventas
            ├── LoginView.vue
            ├── catalog/CatalogView.vue
            ├── sales/SalesView.vue
            ├── inventory/InventoryView.vue
            ├── purchases/PurchasesView.vue
            ├── cash/CashView.vue
            ├── technical-service/TicketsView.vue
            ├── reports/ReportsView.vue
            ├── users/UsersView.vue
            └── admin/                  ← portal de administración maestro
```

---

## 12. Dependencias completas

### Backend Python (`backend/requirements.txt`)

| Paquete | Versión | Rol |
|---------|---------|-----|
| `Django` | 6.0.2 | Framework web |
| `djangorestframework` | 3.16.1 | API REST |
| `django-tenants` | 3.10.0 | Multi-tenancy con schemas PostgreSQL |
| `djangorestframework_simplejwt` | 5.5.1 | Autenticación JWT |
| `psycopg2-binary` | 2.9.11 | Driver PostgreSQL |
| `PyJWT` | 2.11.0 | JWT para token del portal admin |
| `python-dotenv` | 1.2.1 | Carga de `.env` |
| `python-dateutil` | 2.9.0 | Parseo de fechas |
| `asgiref` | 3.11.1 | Soporte ASGI |
| `sqlparse` | 0.5.5 | Parser SQL |
| `tzdata` | 2025.3 | Zonas horarias (America/Guayaquil) |
| `catboost` | ≥ 1.2 | Modelos de predicción (ensemble v22) |
| `joblib` | ≥ 1.2 | Serialización de modelos `.pkl` |
| `meteostat` | ≥ 1.6 | Datos climáticos Quito (lat/lon) |
| `holidays` | ≥ 0.46 | Feriados Ecuador |
| `numpy` | ≥ 1.24 | Cálculo numérico |
| `pandas` | ≥ 2.0 | Manipulación de datos |
| `scipy` | ≥ 1.10 | Funciones matemáticas (Fourier) |
| `openai` | ≥ 1.0 | Cliente GPT-4o mini |
| `anthropic` | ≥ 0.40 | Cliente Claude (alternativa) |
| `plotly` | ≥ 5.0 | Gráficas (notebooks de desarrollo) |

### Frontend Node.js (`frontend/package.json`)

| Paquete | Versión | Rol |
|---------|---------|-----|
| `vue` | ^3.5.28 | Framework UI |
| `vue-router` | ^5.0.3 | Enrutado SPA |
| `pinia` | ^3.0.4 | Estado global |
| `axios` | ^1.13.5 | Cliente HTTP |
| `vite` | ^7.3.1 | Bundler y dev server |
| `typescript` | ~5.9.3 | Tipado estático |
| `vitest` | ^4.0.18 | Testing unitario |

---

## 13. Posibles errores y soluciones

### E1 — `django.db.utils.ProgrammingError: schema "public" already exists`

**Causa**: `setup_public_tenant` ya fue ejecutado anteriormente.

**Solución**: Ignorar el error o verificar que el tenant público ya existe:
```python
# python manage.py shell
from apps.tenants.models import Company
print(Company.objects.filter(schema_name='public').exists())  # debe ser True
```

---

### E2 — `django.db.utils.OperationalError: could not connect to server`

**Causa**: PostgreSQL no está corriendo o las credenciales en `.env` son incorrectas.

**Solución**:
```bash
# Verificar que PostgreSQL está activo
pg_isready -h localhost -p 5432

# Verificar conexión con las credenciales del .env
psql -U postgres -d techhive_db -h localhost
```

---

### E3 — `ModuleNotFoundError: No module named 'catboost'`

**Causa**: El entorno virtual no está activo, o la instalación de catboost falló.

**Solución**:
```bash
source venv/bin/activate
pip install catboost>=1.2
# Si falla en sistemas ARM (Apple Silicon):
pip install catboost --no-binary catboost
```

---

### E4 — `FileNotFoundError: magic_direct_v22.pkl`

**Causa**: Los modelos entrenados no están en `backend/apps/prediccion/ml_models/`.

**Solución**:
```bash
ls backend/apps/prediccion/ml_models/
# Si el directorio está vacío, copiar los archivos .pkl desde la exportación del notebook
# Los archivos necesarios son:
#   magic_direct_v22.pkl, magic_ratio_v22.pkl
#   pap_direct_v22.pkl,   pap_ratio_v22.pkl
#   global_model_v22.pkl, metadata_v22.json
```

---

### E5 — `Unable to resolve hostname demo.localhost`

**Causa**: El archivo de hosts del sistema no tiene la entrada para `demo.localhost`.

**Solución**: Agregar a `/etc/hosts` (Linux/Mac) o `C:\Windows\System32\drivers\etc\hosts` (Windows):
```
127.0.0.1  demo.localhost
127.0.0.1  admin.localhost
```

---

### E6 — `401 Unauthorized` en requests al backend

**Causa**: El token JWT expiró o no se está enviando correctamente.

**Solución**:
```bash
# Renovar el token con el refresh token
curl -X POST "http://demo.localhost:8000/api/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

### E7 — El chatbot responde "No entendí tu mensaje"

**Causa**: El mensaje no coincide con ninguna intención del router regex y `OPENAI_API_KEY` no está configurada.

**Solución**: Verificar que `OPENAI_API_KEY` está en el `.env`, o usar frases que coincidan con las intenciones documentadas (ver sección de endpoints). Ejemplos válidos:
- Staff: `"ventas de hoy"`, `"predicción 7 días"`, `"stock de inventario"`, `"tickets pendientes"`
- Cliente: `"precio del cuaderno"`, `"hay laptops disponibles"`, `"qué categorías tienen"`

---

### E8 — `CORS error` en el frontend (Network Error)

**Causa**: El proxy de Vite no está redirigiendo correctamente al backend.

**Solución**: Verificar que `vite.config.ts` contiene la configuración del proxy:
```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```
Y que el backend está corriendo en el puerto 8000.

---

### E9 — Primera predicción tarda varios segundos

**Causa**: Los modelos CatBoost (~500 MB) se están cargando en memoria por primera vez. El warmup automático corre en un thread daemon al arrancar el servidor pero puede no haber terminado aún.

**Solución**: Es comportamiento esperado. Esperar 5-10 segundos tras arrancar el servidor antes de hacer la primera request de predicción. Las solicitudes siguientes son inmediatas.

---

### E10 — `migrate_schemas` falla con `Table already exists`

**Causa**: Se intenta migrar un schema que ya tiene tablas.

**Solución**:
```bash
# Verificar estado de migraciones para un schema específico
python manage.py showmigrations --schema=demo

# Aplicar solo migraciones pendientes
python manage.py migrate_schemas --schema=demo
```

---

## Pruebas del chatbot

```bash
cd backend
source venv/bin/activate

# Canal staff — 67 casos, 14 intenciones
python apps/chatbot/evaluar_chatbot.py --modo staff

# Canal cliente — 56 casos, 7 intenciones
python apps/chatbot/evaluar_chatbot.py --modo cliente
```

Resultados esperados:

| Canal | Casos totales | Accuracy | Macro Precision | Macro F1 |
|-------|--------------|----------|-----------------|----------|
| Staff | 67 | 100 % | 100 % | 100 % |
| Cliente | 56 | 100 % | 100 % | 100 % |

---

## Roles de usuario

| Rol | Permisos |
|-----|---------|
| `admin` | Acceso total al ERP. Puede gestionar usuarios. |
| `manager` | Igual que admin. |
| `employee` | Acceso a módulos habilitados. Sin gestión de usuarios. |
| `client` | Solo catálogo público (`/catalog`) y chatbot de cliente. |

## Módulos activables por tenant

| Código | Descripción |
|--------|-------------|
| `inventory` | Productos, categorías y perchas |
| `sales` | Registro de ventas con ítems y descuento de stock |
| `purchases` | Compras y proveedores |
| `cash_management` | Sesiones de caja, movimientos y balance |
| `reports` | KPIs, gráficas y reportes exportables |
| `technical_service` | Tickets de servicio técnico |

---

## Documentación técnica extendida

La carpeta [`docs/`](./docs/README.md) contiene 12 documentos con arquitectura detallada, flujos de request completos, análisis de seguridad, riesgos técnicos y guías extendidas de instalación.
