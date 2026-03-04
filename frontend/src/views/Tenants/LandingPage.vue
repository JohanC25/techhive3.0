<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const tenant = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await api.get('/api/public-info/')
    tenant.value = response.data
  } catch (err) {
    console.error('Failed to load tenant info')
  } finally {
    loading.value = false
  }
})

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="landing">
    <div v-if="loading">
      <p>Loading...</p>
    </div>

    <div v-else-if="tenant">
      <h1>{{ tenant.name }}</h1>
      <h2>Your Business Management System</h2>
      <p>
        Secure. Independent. Scalable.
      </p>

      <button @click="goToLogin">
        Login
      </button>
    </div>

    <div v-else>
      <h2>Tenant not found</h2>
    </div>
  </div>
</template>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-family: Arial, sans-serif;
  text-align: center;
  background: #111827;
  color: white;
}

h1 {
  font-size: 40px;
  margin-bottom: 10px;
}

h2 {
  font-weight: 400;
  margin-bottom: 10px;
}

p {
  margin-bottom: 20px;
  opacity: 0.8;
}

button {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 6px;
  background: white;
  color: black;
  transition: 0.2s;
}

button:hover {
  opacity: 0.8;
}
</style>