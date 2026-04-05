# 01 — Arquitectura General

## Diagrama de capas

```
┌─────────────────────────────────────────────────────────┐
│                     NAVEGADOR / CLIENTE                  │
│          Vue 3 + Vite + TypeScript + Pinia              │
│   [LoginView] [DashboardView] [SalesView] [ChatBot.vue] │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/JSON  (Axios + JWT Bearer)
                         │ ws://  (futuro — no implementado)
┌────────────────────────▼────────────────────────────────┐
│                  DJANGO 6 / DRF 3.16                     │
│  TenantMainMiddleware → ModuleAccessMiddleware → View    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │  Apps Core   │  │  Apps Módulos│  │  Chatbot + ML  │ │
│  │  users       │  │  sales       │  │  router.py     │ │
│  │  tenants     │  │  inventory   │  │  handlers.py   │ │
│  │  core        │  │  purchases   │  │  predictor.py  │ │
│  │              │  │  cash_mgmt   │  │  llm_fallback  │ │
│  │              │  │  tech_svc    │  │                │ │
│  │              │  │  reports     │  │                │ │
│  └──────────────┘  └──────────────┘  └───────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ django_tenants.postgresql_backend
┌────────────────────────▼────────────────────────────────┐
│                  POSTGRESQL 14+                          │
│  schema: public       │  schema: magic_world            │
│  ─ tenants_company    │  ─ users_user                   │
│  ─ tenants_domain     │  ─ ventas_venta                 │
│  ─ core_module        │  ─ inventory_product            │
│                       │  ─ ...                          │
│                       │  schema: papeleria              │
│                       │  ─ users_user                   │
│                       │  ─ ventas_venta                 │
│                       │  ─ ...                          │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│             SERVICIOS EXTERNOS                           │
│  OpenAI API (GPT-4o mini)  │  Meteostat (clima Quito)   │
└─────────────────────────────────────────────────────────┘
```

## Componentes principales

### Backend — Django

| Componente | Archivo(s) | Responsabilidad |
|-----------|-----------|----------------|
| Tenant middleware | `django_tenants.middleware.main.TenantMainMiddleware` | Detecta el schema activo por dominio HTTP |
| Module middleware | `apps/core/middleware.py` | Bloquea endpoints de módulos no habilitados para el tenant |
| URL router | `config/tenant_urls.py` | Punto de entrada de todas las rutas `/api/*` |
| Auth | `config/settings.py` (`REST_FRAMEWORK`) | JWT via `rest_framework_simplejwt` |
| Permisos | `apps/core/permissions.py` | `IsNotClient` — bloquea rol `client` en endpoints internos |
| Admin portal | `apps/tenants/views.py` | CRUD de tenants (ADMIN_MASTER_KEY) |

### Backend — ML y Chatbot

| Componente | Archivo | Responsabilidad |
|-----------|---------|----------------|
| Predictor singleton | `apps/prediccion/predictor.py` | Carga 5 `.pkl` + metadata, forecast recursivo v22 |
| Warmup | `apps/prediccion/apps.py` | Pre-carga el predictor en thread daemon al arrancar |
| Staff router | `apps/chatbot/router.py` | 14 intenciones staff via regex |
| Staff handlers | `apps/chatbot/handlers.py` | SQL raw por intención + llamada ML |
| Client router | `apps/chatbot/client_router.py` | 7 intenciones cliente via regex |
| Client handlers | `apps/chatbot/client_handlers.py` | Consultas catálogo (sin exponer costo/SKU) |
| LLM fallback | `apps/chatbot/llm_fallback.py` | Scope guard + GPT-4o mini |

### Frontend — Vue 3

| Componente | Archivo | Responsabilidad |
|-----------|---------|----------------|
| Entry point | `src/main.ts` | Monta app, registra Pinia + router |
| Router | `src/router/index.ts` | Rutas tenant / admin, guards de auth y rol |
| Auth store | `src/stores/auth.ts` | JWT en localStorage, fetchUser, refresh automático |
| API service | `src/services/api.ts` | Axios con interceptor JWT + reintento automático en 401 |
| Layout | `src/components/AppLayout.vue` | Sidebar + zona de contenido |
| Chatbot | `src/components/ChatBot.vue` | Ventana flotante 360×520px, markdown básico |

## Flujo de datos resumido

```
Browser → [JWT header] → TenantMainMiddleware (schema=empresa) →
ModuleAccessMiddleware (¿módulo habilitado?) →
DRF View (IsAuthenticated + IsNotClient) →
Serializer/Handler →
PostgreSQL schema:<empresa> →
Response JSON
```

## Patrones de diseño utilizados

| Patrón | Donde | Descripción |
|--------|-------|-------------|
| Singleton | `predictor.py::get_predictor()` | Un único predictor cargado en memoria |
| Strategy | `chatbot/views.py` | Selección de router/handler según `user.role` |
| Chain of Responsibility | Middleware chain | TenantMain → ModuleAccess → SecurityMiddleware → ... |
| Repository (implícito) | Django ORM + `schema_context` | Aislamiento por schema sin cambiar el código de acceso a datos |
| Observer / Signals | `purchases/signals.py` | `pre_save` en Purchase → CashMovement automático |
