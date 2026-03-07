<template>
  <div class="app-shell">
    <!-- ── Sidebar ── -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-icon">T</div>
        <span class="logo-text">TechHive</span>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- User footer -->
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitials }}</div>
          <div class="user-meta">
            <div class="user-name">{{ auth.fullName || auth.user?.username }}</div>
            <div class="user-role">{{ roleLabel }}</div>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout" title="Cerrar sesión">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </button>
      </div>
    </aside>

    <!-- ── Main area ── -->
    <div class="main-area">
      <!-- Header -->
      <header class="topbar">
        <div class="topbar-left">
          <button class="btn-collapse" @click="sidebarCollapsed = !sidebarCollapsed">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <h1 class="page-title">{{ currentTitle }}</h1>
        </div>
        <div class="topbar-right">
          <div class="topbar-date">{{ currentDate }}</div>
        </div>
      </header>

      <!-- Content -->
      <main class="content">
        <router-view />
      </main>
    </div>

    <!-- ── Toast container ── -->
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          class="toast"
          :class="`toast--${toast.type}`"
          @click="toastStore.remove(toast.id)"
        >
          <span class="toast-icon">{{ toastIcons[toast.type] }}</span>
          <span class="toast-message">{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api'

const auth = useAuthStore()
const toastStore = useToastStore()
const router = useRouter()
const route = useRoute()

const sidebarCollapsed = ref(false)
const enabledModules = ref<string[]>([])

// Todos los módulos posibles con su código de módulo
const allNavItems = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    moduleCode: null, // siempre visible
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>`,
  },
  {
    to: '/sales',
    label: 'Ventas',
    moduleCode: 'sales',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  },
  {
    to: '/inventory',
    label: 'Inventario',
    moduleCode: 'inventory',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>`,
  },
  {
    to: '/purchases',
    label: 'Compras',
    moduleCode: 'purchases',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/></svg>`,
  },
  {
    to: '/cash',
    label: 'Caja',
    moduleCode: 'cash_management',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="5" width="20" height="14" rx="2"/><path stroke-linecap="round" d="M2 10h20"/></svg>`,
  },
  {
    to: '/technical-service',
    label: 'Servicio Técnico',
    moduleCode: 'technical_service',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/></svg>`,
  },
  {
    to: '/reports',
    label: 'Reportes',
    moduleCode: 'reports',
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>`,
  },
  {
    to: '/users',
    label: 'Usuarios',
    moduleCode: null,
    adminOnly: true, // solo admin y manager
    icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>`,
  },
]

const isClient = computed(() => auth.user?.role === 'client')
const isAdminOrManager = computed(() => ['admin', 'manager'].includes(auth.user?.role ?? ''))

// Clientes solo ven el catálogo; el resto filtra por módulos habilitados y rol
const navItems = computed(() => {
  if (isClient.value) {
    return [
      {
        to: '/catalog',
        label: 'Catálogo',
        moduleCode: null,
        icon: `<svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>`,
      },
    ]
  }
  return allNavItems.filter((item) => {
    if ((item as any).adminOnly && !isAdminOrManager.value) return false
    return item.moduleCode === null || enabledModules.value.includes(item.moduleCode)
  })
})

async function loadModules() {
  if (isClient.value) return // clientes no necesitan esta llamada
  try {
    const { data } = await api.get('/users/modules/')
    enabledModules.value = data.map((m: { code: string }) => m.code)
  } catch {
    enabledModules.value = allNavItems.filter((i) => i.moduleCode).map((i) => i.moduleCode as string)
  }
}

onMounted(loadModules)

const toastIcons: Record<string, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

const currentTitle = computed(() => (route.meta.title as string) || 'TechHive')

const currentDate = computed(() =>
  new Date().toLocaleDateString('es-EC', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
)

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  if (u.first_name && u.last_name) return `${u.first_name[0]}${u.last_name[0]}`.toUpperCase()
  return u.username[0].toUpperCase()
})

const roleLabels: Record<string, string> = {
  admin: 'Administrador',
  manager: 'Gerente',
  employee: 'Empleado',
}
const roleLabel = computed(() => roleLabels[auth.user?.role ?? ''] ?? '')

async function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
/* ── Variables ── */
:root {
  --sidebar-w: 260px;
  --sidebar-w-col: 68px;
  --topbar-h: 64px;
}

/* ── Shell ── */
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background: #f1f5f9;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

/* ── Sidebar ── */
.sidebar {
  width: 260px;
  min-width: 260px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  transition: width 0.25s ease, min-width 0.25s ease;
  overflow: hidden;
  z-index: 100;
}
.sidebar.collapsed {
  width: 68px;
  min-width: 68px;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.logo-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  background: #2563eb;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: white;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: white;
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.2s;
}
.collapsed .logo-text { opacity: 0; }

/* ── Nav ── */
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
  overflow-x: hidden;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 10px;
  border-radius: 8px;
  color: #94a3b8;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-item:hover {
  background: #1e293b;
  color: #e2e8f0;
}
.nav-item--active {
  background: #1d4ed8;
  color: white;
}
.nav-icon {
  min-width: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-label {
  opacity: 1;
  transition: opacity 0.2s;
}
.collapsed .nav-label { opacity: 0; pointer-events: none; }

/* ── Footer ── */
.sidebar-footer {
  padding: 12px 10px;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}
.user-avatar {
  width: 34px;
  height: 34px;
  min-width: 34px;
  background: #2563eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: white;
}
.user-meta {
  min-width: 0;
  opacity: 1;
  transition: opacity 0.2s;
}
.collapsed .user-meta { opacity: 0; }
.user-name {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-role {
  font-size: 11px;
  color: #64748b;
  white-space: nowrap;
}
.btn-logout {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  transition: color 0.15s, background 0.15s;
  min-width: 32px;
}
.btn-logout:hover {
  color: #ef4444;
  background: rgba(239,68,68,0.1);
}

/* ── Main Area ── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* ── Topbar ── */
.topbar {
  height: 64px;
  min-height: 64px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  z-index: 10;
}
.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.btn-collapse {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition: background 0.15s;
}
.btn-collapse:hover { background: #f1f5f9; }

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}
.topbar-date {
  font-size: 13px;
  color: #94a3b8;
  text-transform: capitalize;
}

/* ── Content ── */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 28px;
}

/* ── Toasts ── */
.toast-container {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 9999;
  pointer-events: none;
}
.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  pointer-events: all;
  cursor: pointer;
  min-width: 280px;
  max-width: 480px;
}
.toast--success { background: #0f172a; color: #4ade80; border: 1px solid #166534; }
.toast--error   { background: #0f172a; color: #f87171; border: 1px solid #991b1b; }
.toast--warning { background: #0f172a; color: #fbbf24; border: 1px solid #92400e; }
.toast--info    { background: #0f172a; color: #60a5fa; border: 1px solid #1e40af; }

.toast-icon { font-weight: 700; font-size: 15px; }
.toast-message { flex: 1; }

/* ── Toast transitions ── */
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { opacity: 0; transform: translateY(16px); }
.toast-leave-to   { opacity: 0; transform: translateY(-8px); }
</style>
