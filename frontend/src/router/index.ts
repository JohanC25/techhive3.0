import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import LandingView from '@/views/Company/LandingPage.vue'
import LoginView from '@/views/Company/LoginPage.vue'
import DashboardView from '@/views/Company/DashboardPage.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Landing',
    component: LandingView,
  },
  { path: '/login', component: LoginView },
  { path: '/dashboard', component: DashboardView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router