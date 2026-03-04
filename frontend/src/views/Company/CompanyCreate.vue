<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const name = ref('')
const schema_name = ref('')
const domain = ref('')
const admin_email = ref('')
const admin_password = ref('')

const createCompany = async () => {
  await api.post('/api/companies/', {
    name: name.value,
    schema_name: schema_name.value,
    domain: domain.value,
    admin_email: admin_email.value,
    admin_password: admin_password.value
  })

  router.push('/companies')
}
</script>

<template>
  <div class="page">
    <h2>Create Company</h2>

    <input v-model="name" placeholder="Company Name" />
    <input v-model="schema_name" placeholder="Schema Name" />
    <input v-model="domain" placeholder="Domain (tenant1.localhost)" />
    <input v-model="admin_email" placeholder="Admin Email" />
    <input v-model="admin_password" type="password" placeholder="Admin Password" />

    <button @click="createCompany">Create</button>
  </div>
</template>

<style scoped>
.page { padding: 40px; }
input { display:block; margin:10px 0; padding:8px; }
</style>