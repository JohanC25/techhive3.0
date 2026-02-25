<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'


const data = ref(null)
const router = useRouter()

import api from '@/services/api'

onMounted(async () => {
  try {
    const response = await api.get('/')
    data.value = response.data
  } catch (error) {
    console.error(error)
  }
})

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="landing" v-if="data">
    <h1>{{ data.company }}</h1>
    <h2>{{ data.headline }}</h2>
    <p>{{ data.subheadline }}</p>

    <ul>
      <li v-for="feature in data.features" :key="feature">
        {{ feature }}
      </li>
    </ul>

    <button @click="goToLogin">
      Login
    </button>
  </div>
</template>

<style>
.landing {
  text-align: center;
  padding: 50px;
}
</style>