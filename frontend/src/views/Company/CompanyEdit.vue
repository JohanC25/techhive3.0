<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

const route = useRoute()
const company = ref<any>(null)

onMounted(async () => {
  const response = await api.get('/api/companies/')
  company.value = response.data.find(
    (c: any) => c.id === Number(route.params.id)
  )
})
</script>

<template>
  <div class="page" v-if="company">
    <h2>{{ company.name }}</h2>
    <p>Schema: {{ company.schema }}</p>
    <p>On Trial: {{ company.on_trial }}</p>
  </div>
</template>

<style scoped>
.page { padding: 40px; }
</style>