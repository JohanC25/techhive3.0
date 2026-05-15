<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const tenant = ref<any>(null)
const error = ref('')

const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/login')
}

const fetchTenantInfo = async () => {
  try {
    // Esta ruta en tu backend devuelve { "company": "...", "message": "..." }
    const response = await api.get('/api/public-info/')
    tenant.value = response.data
  } catch (err) {
    error.value = 'Error al cargar la información de la empresa'
  }
}

onMounted(fetchTenantInfo)
</script>

<template>
  <div class="dashboard">
    <header>
      <h2 v-if="tenant">Panel de {{ tenant.company }}</h2>
      <button class="logout-btn" @click="logout">Cerrar Sesión</button>
    </header>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="tenant">
      <!-- <p class="welcome-msg">{{ tenant.message }}</p> -->

      <div class="cards">
        <div class="card">Módulo de Usuarios</div>
        <div class="card">Módulo de Ventas</div>
        <div class="card">Módulo de Inventario</div>
        
        <div class="card ai-card">
          <h3>Asistente Chatbot</h3>
          <button class="action-btn" @click="router.push('/chatbot')">Abrir Chat</button>
        </div>

        <div class="card ai-card">
            <h3>Reporte IA Ventas</h3>
            <button class="action-btn" @click="router.push('/reporte-ia')">Ver Reporte</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 40px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px solid #eee;
  padding-bottom: 20px;
}

.welcome-msg {
  color: #666;
  margin-top: 10px;
}

.cards {
  margin-top: 30px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.card {
  padding: 24px;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.ai-card {
  background: #f0f7ff; /* Color sutilmente diferente para resaltar IA */
  border: 1px solid #3b82f6;
}

.ai-card h3 {
  margin-top: 0;
  color: #1e40af;
  font-size: 1.1rem;
}

.logout-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.action-btn {
  margin-top: 12px;
  width: 100%;
  padding: 10px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.action-btn:hover {
  background: #2563eb;
}

.error {
  color: #dc2626;
  background: #fee2e2;
  padding: 10px;
  border-radius: 6px;
  margin-top: 20px;
}
</style>