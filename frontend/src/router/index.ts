import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// Platform (mysaas.com)
import CompanyLanding from '@/views/Company/LandingPage.vue'
import CompanyLogin from '@/views/Company/LoginPage.vue'
import CompanyDashboard from '@/views/Company/DashboardPage.vue'
import CompaniesList from '@/views/Company/CompaniesList.vue'
import CompanyCreate from '@/views/Company/CompanyCreate.vue'
import CompanyEdit from '@/views/Company/CompanyEdit.vue'
import CompanyView from '@/views/Company/CompanyView.vue'

// Tenant (tenant1.mysaas.com)
import TenantLanding from '@/views/Tenants/LandingPage.vue'
import TenantLogin from '@/views/Tenants/LoginPage.vue'
import TenantDashboard from '@/views/Tenants/DashboardPage.vue'
import ChatBot from '@/views/Tenants/ChatBot.vue'
import ReporteIA from '@/views/Tenants/ReporteIA.vue'

const hostname = window.location.hostname

// Detect subdomain
const isTenant =
  hostname !== 'localhost' &&
  !hostname.startsWith('www') &&
  hostname.includes('.')

let routes: Array<RouteRecordRaw>

if (isTenant) {
  //Rutas para empresas (tenants)
  routes = [
    { path: '/', name: 'TenantLanding', component: TenantLanding },
    { path: '/login', name: 'TenantLogin', component: TenantLogin },
    { path: '/dashboard', name: 'TenantDashboard', component: TenantDashboard },
    
    { path: '/chatbot', name: 'ChatBot', component: ChatBot },
    { path: '/reporte-ia', name: 'ReporteIA', component: ReporteIA },
  ]
} else {
  //Rutas para admin
  routes = [
    { path: '/', name: 'Landing', component: CompanyLanding },
    { path: '/login', name: 'Login', component: CompanyLogin },
    { path: '/dashboard', name: 'Dashboard', component: CompanyDashboard },

    //Companies
    { path: '/companies', redirect: '/companies/' },
    { path: '/companies/', name: 'CompaniesList', component: CompaniesList },
    { path: '/companies/create', name: 'CompanyCreate', component: CompanyCreate },
    { path: '/companies/:id', name: 'CompanyView', component: CompanyView },
    { path: '/companies/:id/edit', name: 'CompanyEdit', component: CompanyEdit },
  ]
}

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 🔐 Route Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access')

  const protectedRoutes = ['/dashboard']

  if (protectedRoutes.includes(to.path) && !token) {
    return next('/login')
  }

  next()
})

export default router