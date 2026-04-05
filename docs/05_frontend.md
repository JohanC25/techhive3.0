# 05 — Frontend

## Stack tecnológico

| Tecnología | Versión | Rol |
|-----------|---------|-----|
| Vue 3 | 3.5.28 | Framework reactivo (Composition API) |
| Vite | 7.3 | Bundler y servidor de desarrollo |
| TypeScript | 5.9 | Tipado estático |
| Pinia | 3.0 | Gestión de estado global |
| Vue Router | 5.0 | Enrutado SPA |
| Axios | 1.13 | Cliente HTTP |
| Vitest | 4.0 | Testing unitario |

Sin librerías de UI externas: todos los componentes visuales (gráficas, modales, tablas) están implementados en HTML/CSS nativo.

## Estructura de archivos

```
frontend/src/
├── main.ts                    ← Entry point (Pinia + Router + App)
├── App.vue                    ← Root component
├── assets/
│   └── crud.css               ← Estilos globales para tablas CRUD
├── components/
│   ├── AppLayout.vue          ← Sidebar + contenido principal
│   └── ChatBot.vue            ← Widget flotante del chatbot
├── router/
│   └── index.ts               ← Rutas + guards de navegación
├── services/
│   ├── api.ts                 ← Axios con JWT + refresh automático
│   └── adminApi.ts            ← Axios para el portal admin (master key)
├── stores/
│   ├── auth.ts                ← Pinia: sesión JWT del tenant
│   ├── adminStore.ts          ← Pinia: sesión del portal admin
│   └── toast.ts               ← Pinia: notificaciones toast
└── views/
    ├── LoginView.vue          ← Login de tenant
    ├── DashboardView.vue      ← KPIs + gráfica de ventas
    ├── catalog/
    │   └── CatalogView.vue    ← Catálogo público (solo role=client)
    ├── sales/
    │   └── SalesView.vue      ← CRUD ventas + ítems + cliente
    ├── inventory/
    │   └── InventoryView.vue  ← CRUD productos + categorías + perchas
    ├── purchases/
    │   └── PurchasesView.vue  ← CRUD compras + proveedores
    ├── cash/
    │   └── CashView.vue       ← Caja: apertura de sesión + movimientos
    ├── technical-service/
    │   └── TicketsView.vue    ← Tickets de servicio técnico
    ├── reports/
    │   └── ReportsView.vue    ← Reportes y exportación
    ├── users/
    │   └── UsersView.vue      ← CRUD usuarios + auto-username
    └── admin/
        ├── AdminLoginView.vue ← Login con master key
        ├── AdminLayout.vue    ← Layout del portal admin
        └── CompaniesView.vue  ← Gestión de empresas/tenants
```

## Router (`src/router/index.ts`)

### Detección de portal

```typescript
const hostname = window.location.hostname
export const IS_ADMIN_PORTAL =
  hostname === 'admin.localhost' || hostname.startsWith('admin.')
```

La misma build de Vue sirve tanto el portal de tenants como el portal admin. La detección se hace en tiempo de ejecución por hostname.

### Rutas del tenant

```
/login          → LoginView (guest)
/               → redirect /dashboard
/dashboard      → DashboardView  (requiresAuth)
/catalog        → CatalogView    (requiresAuth — solo clientes)
/sales          → SalesView      (requiresAuth)
/inventory      → InventoryView  (requiresAuth)
/purchases      → PurchasesView  (requiresAuth)
/cash           → CashView       (requiresAuth)
/technical-service → TicketsView (requiresAuth)
/reports        → ReportsView    (requiresAuth)
/users          → UsersView      (requiresAuth)
```

### Guards de navegación

```typescript
router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  const isClient = auth.user?.role === 'client'

  if (to.meta.requiresAuth && !auth.isAuthenticated) return next('/login')

  // Clientes solo pueden acceder a /catalog
  if (auth.isAuthenticated && isClient && to.name !== 'catalog') {
    return next('/catalog')
  }

  // Al loguearse, clientes van a /catalog, staff a /dashboard
  if (to.meta.guest && auth.isAuthenticated) {
    return next(isClient ? '/catalog' : '/dashboard')
  }

  next()
})
```

## Stores (Pinia)

### `auth.ts`

```typescript
interface AuthUser {
  id: number; username: string; first_name: string; last_name: string;
  email: string; role: 'admin' | 'manager' | 'employee' | 'client'; phone: string;
}
```

- `token`: almacenado en `localStorage` como `access_token`
- `login()`: POST `/api/login/` → guarda tokens → llama `fetchUser()`
- `fetchUser()`: GET `/api/users/me/` → hidrata `user`
- `logout()`: limpia localStorage y estado
- Al inicializar la store: si hay token en localStorage, se llama `fetchUser()` automáticamente (restaura sesión)

### `toast.ts`

Store de notificaciones efímeras (tipo toast/snackbar) con auto-dismiss.

### `adminStore.ts`

Equivalente a `auth.ts` pero para el portal admin. Usa `ADMIN_MASTER_KEY` en lugar de credenciales de usuario.

## Servicio HTTP (`src/services/api.ts`)

```typescript
const api = axios.create({ baseURL: '/api', timeout: 15000 })
```

**Interceptor de request**: inyecta `Authorization: Bearer <token>` en cada petición.

**Interceptor de response** (refresh automático en 401):
1. Si recibe `401` y no es retry → intenta `POST /api/refresh/`
2. Si el refresh tiene éxito: actualiza token y reintenta la petición original
3. Si el refresh falla: limpia localStorage y redirige a `/login`
4. Las peticiones en cola durante el refresh se resuelven todas juntas con el nuevo token (patrón `failedQueue`)

## Vistas clave

### `DashboardView.vue`
- 4 tarjetas KPI con skeleton loading (ventas, caja, inventario, servicio técnico)
- Selector de período: hoy / semana / mes / año
- Gráfica de barras nativa (canvas/SVG sin librería) de ventas por día
- `Promise.all([dashboard, chart])` para llamadas paralelas al backend

### `ChatBot.vue`
- Botón flotante en esquina inferior derecha
- Ventana 360×520px con animación de entrada
- `esCliente` computed: cambia título y sugerencias según `auth.user?.role === 'client'`
- Indicador de escritura (3 puntos animados)
- Renderizado básico de markdown: negritas, cursiva, saltos de línea
- `session_id` UUID persistido en `ref()` por instancia de componente
- POST a `/api/chatbot/mensaje/` en cada envío

### `SalesView.vue`
- Tabla de ventas con modal de creación/edición
- Formulario multi-ítem: agregar/quitar líneas de productos
- Campo cliente: select de usuarios con `role=client`
- Total calculado en tiempo real en el frontend como suma de subtotales
- Descuento de stock gestionado en el backend al crear

### `CashView.vue`
- Al montar: GET `/api/cash/sessions/today/`
  - Si 404 → modal obligatorio "Apertura de caja" (monto inicial)
  - Si existe → muestra info de sesión (hora, monto inicial)
- Balance: `caja_final = monto_inicial + ingresos − egresos`

### `InventoryView.vue`
- Tabs: Productos / Categorías / Perchas
- Formulario de producto incluye select de percha (Shelf)

## Proxy de desarrollo (Vite)

El frontend en desarrollo usa el proxy de Vite para redirigir `/api/*` al backend en `localhost:8000`. La configuración exacta está en `vite.config.ts`.

## Testing

```bash
npm run test:unit    # Vitest
npm run lint         # oxlint + eslint
npm run type-check   # vue-tsc
npm run build        # build de producción con type-check
```

Un test unitario existe en `src/__tests__/App.spec.ts` (boilerplate generado por Vite).
