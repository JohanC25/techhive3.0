# 08 — Estructura de Carpetas Explicada

## Árbol raíz

```
techhive3.0/
├── backend/                    ← Servidor Django
├── frontend/                   ← SPA Vue 3
├── docs/                       ← Esta documentación
├── ModeloPrediccionVentasFinalDjango.ipynb  ← Notebook ML (desarrollo del modelo)
├── README.md                   ← Inicio rápido
├── BACKEND_PARTE1.txt          ← Exportación de código para evaluación académica
├── BACKEND_PARTE2.txt
└── FRONTEND.txt
```

---

## Backend

```
backend/
├── manage.py                   ← CLI de Django
├── requirements.txt            ← Dependencias Python con versiones fijadas
├── .env                        ← Variables de entorno (no en git)
│
├── config/                     ← Configuración del proyecto Django
│   ├── settings.py             ← SHARED_APPS, TENANT_APPS, DATABASES, MIDDLEWARE
│   ├── tenant_urls.py          ← ROOT_URLCONF: todas las rutas /api/* de tenants
│   ├── public_urls.py          ← PUBLIC_SCHEMA_URLCONF: rutas del portal admin
│   └── wsgi.py                 ← Entry point WSGI para producción
│
└── apps/
    ├── core/                   ← App compartida (schema public)
    │   ├── models.py           ← Module (catálogo de módulos disponibles)
    │   ├── permissions.py      ← IsNotClient
    │   ├── middleware.py       ← ModuleAccessMiddleware
    │   └── management/
    │       └── commands/
    │           ├── seed_demo.py         ← Poblar tenant demo con datos de prueba
    │           ├── seed_modules.py      ← Insertar módulos en tabla core_module
    │           └── setup_public_tenant.py  ← Crear tenant 'public' inicial
    │
    ├── tenants/                ← App compartida (schema public)
    │   ├── models.py           ← Company (TenantMixin), Domain (DomainMixin)
    │   ├── views.py            ← Admin CRUD: CompanyListView, CompanyDetailView
    │   ├── admin_auth.py       ← @admin_required, create_admin_token (master key JWT)
    │   └── apps.py
    │
    ├── users/                  ← App por tenant
    │   ├── models.py           ← User (AbstractUser + role, phone, cedula)
    │   ├── serializers.py      ← UserSerializer, UserCreateSerializer (auto-username)
    │   ├── views.py            ← UserViewSet (me, modules, change-password)
    │   └── urls.py
    │
    ├── chatbot/                ← App por tenant
    │   ├── models.py           ← ChatSession, ChatMessage
    │   ├── views.py            ← enviar_mensaje(), historial_sesion(), limpiar_sesion()
    │   ├── router.py           ← 14 intenciones staff (regex INTENT_PATTERNS)
    │   ├── handlers.py         ← SQL handlers staff (14 funciones + HANDLERS dict)
    │   ├── client_router.py    ← 7 intenciones cliente (regex PRIORITY_ORDER)
    │   ├── client_handlers.py  ← Handlers cliente (SQL catálogo seguro)
    │   ├── llm_fallback.py     ← is_in_domain(), fallback_staff(), fallback_cliente()
    │   ├── evaluar_chatbot.py  ← 123 casos de prueba, métricas Accuracy/F1
    │   ├── apps.py             ← ChatbotConfig (registra señales)
    │   └── urls.py             ← mensaje/, historial/, health/
    │
    ├── prediccion/             ← App por tenant
    │   ├── predictor.py        ← TechHivePredictor singleton, forecast v22
    │   ├── views.py            ← PrediccionView (GET ?dias=N)
    │   ├── apps.py             ← warmup en thread daemon al arrancar
    │   ├── urls.py
    │   └── ml_models/          ← Modelos entrenados (archivos .pkl + metadata)
    │       ├── magic_direct_v22.pkl
    │       ├── magic_ratio_v22.pkl
    │       ├── pap_direct_v22.pkl
    │       ├── pap_ratio_v22.pkl
    │       ├── global_v22.pkl
    │       └── metadata_v22.json   ← pesos, calibraciones, métricas
    │
    └── modules/                ← Módulos del ERP (todos por tenant)
        ├── sales/
        │   ├── models.py       ← Venta, VentaItem
        │   ├── serializers.py  ← VentaSerializer (nested items, create/update)
        │   ├── views.py        ← VentaViewSet, VentaItemViewSet
        │   ├── signals.py      ← Minimal (CashMovement creado en serializer)
        │   ├── apps.py
        │   ├── urls.py
        │   └── management/commands/cargar_ventas.py  ← importar CSV histórico
        │
        ├── inventory/
        │   ├── models.py       ← Category, Shelf, Product
        │   ├── serializers.py  ← ProductSerializer (con shelf_name), ShelfSerializer
        │   ├── views.py        ← ProductViewSet (con catalog action), ShelfViewSet
        │   ├── urls.py
        │   └── migrations/
        │       ├── 0001_initial.py
        │       ├── 0002_shelf.py        ← añade modelo Shelf
        │       └── 0003_seed_categories.py  ← RunPython: Servicio, Producto, Reparación
        │
        ├── purchases/
        │   ├── models.py       ← Supplier, Purchase, PurchaseItem
        │   ├── serializers.py  ← PurchaseSerializer (nested items)
        │   ├── signals.py      ← pre_save Purchase: → CashMovement al recibir
        │   ├── views.py        ← PurchaseViewSet, SupplierViewSet
        │   └── apps.py         ← registra señales en ready()
        │
        ├── cash_management/
        │   ├── models.py       ← CashSession, CashMovement
        │   ├── serializers.py  ← CashSessionSerializer, CashMovementSerializer
        │   ├── views.py        ← CashSessionViewSet (today action), CashMovementViewSet (balance)
        │   └── urls.py
        │
        ├── technical_service/
        │   ├── models.py       ← ServiceTicket (6 estados, 4 prioridades)
        │   ├── serializers.py
        │   ├── views.py        ← ServiceTicketViewSet
        │   └── urls.py
        │
        └── reports/
            ├── views.py        ← dashboard_summary, ventas_por_dia, compras_resumen
            └── urls.py
```

---

## Frontend

```
frontend/
├── package.json                ← Dependencias NPM y scripts
├── vite.config.ts              ← Configuración Vite (proxy /api → :8000)
├── tsconfig*.json              ← Configuración TypeScript
├── eslint.config.ts            ← ESLint + oxlint
│
└── src/
    ├── main.ts                 ← Monta App, registra Pinia + Router
    ├── App.vue                 ← Root component (RouterView)
    │
    ├── assets/
    │   └── crud.css            ← Estilos tablas, modales, botones
    │
    ├── components/
    │   ├── AppLayout.vue       ← Sidebar (nav items por módulo), header, RouterView
    │   └── ChatBot.vue         ← Widget flotante (360×520px, markdown, typing)
    │
    ├── router/
    │   └── index.ts            ← IS_ADMIN_PORTAL, adminRoutes, tenantRoutes, guards
    │
    ├── services/
    │   ├── api.ts              ← Axios tenant: JWT inyectado, refresh en 401
    │   └── adminApi.ts         ← Axios admin: master key en headers
    │
    ├── stores/
    │   ├── auth.ts             ← Pinia: user (AuthUser), token, login/logout/fetchUser
    │   ├── adminStore.ts       ← Pinia: token admin, login admin
    │   └── toast.ts            ← Pinia: cola de notificaciones toast
    │
    └── views/
        ├── LoginView.vue           ← Formulario login tenant
        ├── DashboardView.vue       ← KPIs + gráfica (4 KPI cards, bar chart nativo)
        ├── catalog/CatalogView.vue ← Solo clientes: lista de productos con filtro
        ├── sales/SalesView.vue     ← CRUD ventas + ítems + cliente FK
        ├── inventory/InventoryView.vue  ← Tabs: Productos / Categorías / Perchas
        ├── purchases/PurchasesView.vue  ← CRUD compras + proveedores
        ├── cash/CashView.vue       ← Apertura de caja + movimientos + balance
        ├── technical-service/TicketsView.vue  ← CRUD tickets
        ├── reports/ReportsView.vue ← Reportes con selector de período
        ├── users/UsersView.vue     ← CRUD usuarios + cédula + auto-username
        └── admin/
            ├── AdminLoginView.vue  ← Login con master key
            ├── AdminLayout.vue     ← Layout del portal admin
            └── CompaniesView.vue   ← CRUD empresas + módulos activos
```

---

## Archivos de configuración raíz

| Archivo | Descripción |
|---------|-------------|
| `backend/.env` | `SECRET_KEY`, `DB_*`, `OPENAI_API_KEY`, `ADMIN_MASTER_KEY` (no en git) |
| `backend/.env.example` | Plantilla de variables de entorno |
| `backend/requirements.txt` | 22 dependencias Python con versiones exactas |
| `frontend/package.json` | 4 deps runtime + 16 devDeps |
| `frontend/vite.config.ts` | Proxy `/api → localhost:8000` |
