import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/adminStore'

// Detección de modo: admin.localhost → portal admin, resto → app tenant
const hostname = window.location.hostname
export const IS_ADMIN_PORTAL = hostname === 'admin.localhost' || hostname.startsWith('admin.')

const adminRoutes = [
  {
    path: '/login',
    name: 'admin-login',
    component: () => import('@/views/admin/AdminLoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAdminAuth: true },
    children: [
      {
        path: '',
        name: 'admin-companies',
        component: () => import('@/views/admin/CompaniesView.vue'),
        meta: { title: 'Empresas' },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const tenantRoutes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('@/components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: 'Dashboard' } },
      { path: 'sales', name: 'sales', component: () => import('@/views/sales/SalesView.vue'), meta: { title: 'Ventas' } },
      { path: 'inventory', name: 'inventory', component: () => import('@/views/inventory/InventoryView.vue'), meta: { title: 'Inventario' } },
      { path: 'purchases', name: 'purchases', component: () => import('@/views/purchases/PurchasesView.vue'), meta: { title: 'Compras' } },
      { path: 'cash', name: 'cash', component: () => import('@/views/cash/CashView.vue'), meta: { title: 'Caja' } },
      { path: 'technical-service', name: 'technical-service', component: () => import('@/views/technical-service/TicketsView.vue'), meta: { title: 'Servicio Técnico' } },
      { path: 'reports', name: 'reports', component: () => import('@/views/reports/ReportsView.vue'), meta: { title: 'Reportes' } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: IS_ADMIN_PORTAL ? adminRoutes : tenantRoutes,
})

router.beforeEach((to, _from, next) => {
  if (IS_ADMIN_PORTAL) {
    const admin = useAdminStore()
    if (to.meta.requiresAdminAuth && !admin.isAuthenticated) return next('/login')
    if (to.meta.guest && admin.isAuthenticated) return next('/')
    return next()
  }
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return next('/login')
  if (to.meta.guest && auth.isAuthenticated) return next('/dashboard')
  next()
})

export default router
