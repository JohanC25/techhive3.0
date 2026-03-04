<script setup lang="ts">
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { ref, onMounted } from 'vue'

const router = useRouter()
const companies = ref<any[]>([])
const error = ref('')

// 🔐 Logout
const logout = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  router.push('/login')
}

// ➡ Navigate to Companies List
const goToCompanies = () => {
  router.push('/companies/')
}

// 📡 Fetch companies for dashboard preview
const fetchCompanies = async () => {
  try {
    const response = await api.get('/api/companies/')
    companies.value = response.data
  } catch (err) {
    error.value = 'Unauthorized or failed to load companies'
  }
}

onMounted(fetchCompanies)
</script>

<template>
  <div class="dashboard">
    <header>
      <h2>Platform Dashboard</h2>

      <div class="actions">
        <button @click="goToCompanies">Manage Companies</button>
        <button @click="logout">Logout</button>
      </div>
    </header>

    <div v-if="error" class="error">
      {{ error }}
    </div>

    <div v-if="companies.length">
      <h3>Registered Companies</h3>
      <ul>
        <li v-for="company in companies" :key="company.id">
          {{ company.name }} ({{ company.schema }})
        </li>
      </ul>
    </div>

    <div v-else>
      <p>No companies found.</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 40px;
  font-family: Arial, sans-serif;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  display: flex;
  gap: 10px;
}

button {
  padding: 8px 14px;
  cursor: pointer;
  border: none;
  border-radius: 6px;
  background-color: #111827;
  color: white;
  transition: 0.2s;
}

button:hover {
  opacity: 0.85;
}

ul {
  margin-top: 20px;
}

.error {
  color: red;
  margin-top: 15px;
}
</style>