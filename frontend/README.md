# Frontend — TechHive 3.0

Vue 3 + Vite + TypeScript. SPA que sirve tanto el portal admin (gestión de empresas) como el ERP de cada tenant.

## Stack

- **Vue 3.5** con Composition API y `<script setup>`
- **Vite 7** como bundler
- **TypeScript 5.9**
- **Pinia 3** para gestión de estado
- **Vue Router 5**
- **Axios** para peticiones HTTP

## Instalación

```bash
cd frontend
npm install
```

## Variables de entorno

Crear un archivo `.env` en `frontend/` (opcional — los valores por defecto funcionan para desarrollo local):

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Scripts disponibles

| Comando              | Descripción                                      |
|----------------------|--------------------------------------------------|
| `npm run dev`        | Servidor de desarrollo con HMR en `:5173`        |
| `npm run build`      | Build de producción (type-check + build)         |
| `npm run preview`    | Preview del build de producción en `:4173`       |
| `npm run type-check` | Verificación de tipos con vue-tsc                |
| `npm run lint`       | Linting con oxlint + eslint (con autofix)        |
| `npm run format`     | Formateo con Prettier                            |
| `npm run test:unit`  | Tests unitarios con Vitest                       |

## Estructura de vistas

```
src/
├── views/
│   ├── LoginView.vue               Inicio de sesión tenant
│   ├── DashboardView.vue           Dashboard principal
│   ├── admin/
│   │   ├── AdminLoginView.vue      Login con ADMIN_MASTER_KEY
│   │   ├── AdminLayout.vue         Layout del portal admin
│   │   └── CompaniesView.vue       CRUD de empresas y módulos
│   ├── catalog/
│   │   └── CatalogView.vue         Catálogo público (accesible a clientes)
│   ├── inventory/                  Gestión de inventario (staff+)
│   ├── sales/                      Ventas (staff+)
│   ├── purchases/                  Compras (staff+)
│   ├── cash/                       Caja (staff+)
│   ├── reports/                    Reportes (staff+)
│   ├── technical-service/          Servicio técnico (staff+)
│   └── users/                      Gestión de usuarios (admin)
├── stores/
│   ├── auth.ts                     Estado de autenticación JWT + rol de usuario
│   ├── adminStore.ts               Estado del portal admin (token admin, empresas)
│   └── toast.ts                    Notificaciones toast globales
└── components/
    └── ChatBot.vue                 Chatbot flotante (staff: ventas, cliente: catálogo)
```

## Rutas principales

| Ruta                      | Componente             | Acceso             |
|---------------------------|------------------------|--------------------|
| `/login`                  | LoginView              | Público            |
| `/dashboard`              | DashboardView          | Autenticado        |
| `/catalog`                | CatalogView            | Autenticado        |
| `/inventory`              | inventory/...          | Staff + Admin      |
| `/sales`                  | sales/...              | Staff + Admin      |
| `/purchases`              | purchases/...          | Staff + Admin      |
| `/cash`                   | cash/...               | Staff + Admin      |
| `/reports`                | reports/...            | Staff + Admin      |
| `/technical-service`      | technical-service/...  | Staff + Admin      |
| `/users`                  | users/...              | Solo Admin         |
| `/admin`                  | AdminLoginView         | Público (admin)    |
| `/admin/companies`        | CompaniesView          | Admin autenticado  |

## Autenticación

El store `auth.ts` gestiona:
- Tokens JWT (access + refresh) almacenados en `localStorage`
- Renovación automática del access token con el refresh token
- Datos del usuario: `id`, `email`, `role` (`admin` | `staff` | `client`)
- Guard de navegación: redirige a `/login` si no hay sesión activa

El store `adminStore.ts` gestiona:
- Token del portal admin (independiente del JWT de tenant)
- Lista de empresas y módulos disponibles
- CRUD de empresas vía la API admin del backend

## Chatbot

El componente `ChatBot.vue` aparece como botón flotante en todas las vistas autenticadas. Detecta el rol del usuario y adapta su comportamiento:

- **Staff/Admin**: título "Asistente TechHive", sugerencias orientadas a consultas de ventas
- **Cliente**: título "Asistente de Compras", sugerencias orientadas a búsqueda de productos

El historial se mantiene por `session_id` (UUID generado al primer mensaje de cada conversación).

## Acceso multi-tenant en desarrollo

El backend identifica el tenant por el header `Host`. Para probar diferentes tenants localmente:

1. Agregar entradas en el archivo `hosts` del sistema operativo:
   ```
   127.0.0.1   empresa1.localhost
   127.0.0.1   empresa2.localhost
   ```
2. Acceder a `http://empresa1.localhost:5173`

El portal admin siempre usa `http://localhost:5173/admin` (sin subdominio de tenant).

## IDE recomendado

- [VS Code](https://code.visualstudio.com/) + extensión [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)
- Desactivar Vetur si está instalado (conflicto con Volar)
