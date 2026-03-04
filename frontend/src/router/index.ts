import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: 'Dashboard' },
        },
        {
          path: 'sales',
          name: 'sales',
          component: () => import('@/views/sales/SalesView.vue'),
          meta: { title: 'Ventas' },
        },
        {
          path: 'inventory',
          name: 'inventory',
          component: () => import('@/views/inventory/InventoryView.vue'),
          meta: { title: 'Inventario' },
        },
        {
          path: 'purchases',
          name: 'purchases',
          component: () => import('@/views/purchases/PurchasesView.vue'),
          meta: { title: 'Compras' },
        },
        {
          path: 'cash',
          name: 'cash',
          component: () => import('@/views/cash/CashView.vue'),
          meta: { title: 'Caja' },
        },
        {
          path: 'technical-service',
          name: 'technical-service',
          component: () => import('@/views/technical-service/TicketsView.vue'),
          meta: { title: 'Servicio Técnico' },
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('@/views/reports/ReportsView.vue'),
          meta: { title: 'Reportes' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && auth.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
