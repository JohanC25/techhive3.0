<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const companies = ref<any[]>([])

const fetchCompanies = async () => {
  const response = await api.get('/api/companies/')
  companies.value = response.data
}

const goToCreate = () => router.push('/companies/create')
const goToView = (id: number) => router.push(`/companies/${id}`)
const goToEdit = (id: number) => router.push(`/companies/${id}/edit`)

onMounted(fetchCompanies)
</script>

<template>
  <div class="page">
    <h2>Companies</h2>

    <button @click="goToCreate">+ Create Company</button>

    <ul>
      <li v-for="company in companies" :key="company.id">
        <strong>{{ company.name }}</strong>
        ({{ company.schema }})

        <button @click="goToView(company.id)">View</button>
        <button @click="goToEdit(company.id)">Edit</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.page { padding: 40px; }
button { margin-left: 10px; }
</style>