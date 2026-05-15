<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
  error.value = ''
  loading.value = true

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
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <h2>Admin Login</h2>

    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />

    <button @click="login" :disabled="loading">
      {{ loading ? 'Logging in...' : 'Login' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
.login {
  text-align: center;
  margin-top: 120px;
}

input {
  display: block;
  margin: 10px auto;
  padding: 8px;
  width: 250px;
}

button {
  padding: 10px 20px;
  cursor: pointer;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>