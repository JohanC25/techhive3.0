<template>
  <div class="admin-app">
    <!-- Top navbar -->
    <header class="navbar">
      <div class="navbar-brand">
        <div class="brand-icon">T</div>
        <span class="brand-name">TechHive <span class="brand-badge">Admin</span></span>
      </div>
      <button class="btn-logout" @click="handleLogout">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        Cerrar sesión
      </button>
    </header>

    <!-- Main content -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/adminStore'

const admin = useAdminStore()
const router = useRouter()

function handleLogout() {
  admin.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-app {
  min-height: 100vh;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #0f172a;
  padding: 0 32px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 36px; height: 36px;
  background: #7c3aed;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 800; color: white;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-badge {
  background: #7c3aed;
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  background: rgba(255,255,255,0.08);
  color: #cbd5e1;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-logout:hover {
  background: rgba(239,68,68,0.2);
  color: #fca5a5;
  border-color: rgba(239,68,68,0.3);
}

.main-content {
  flex: 1;
  padding: 32px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}
</style>
