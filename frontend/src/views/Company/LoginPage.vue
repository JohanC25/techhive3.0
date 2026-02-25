<script setup lang="ts">
import { ref } from 'vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

const login = async () => {
  try {
    const response = await api.post('/api/login/', {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('access', response.data.access)
    localStorage.setItem('refresh', response.data.refresh)

    router.push('/dashboard')

  } catch (err) {
    error.value = 'Invalid credentials'
  }
}
</script>

<template>
  <div>
    <h2>Login</h2>

    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />

    <button @click="login">Login</button>

    <p v-if="error">{{ error }}</p>
  </div>
</template>