<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

// Cambiamos cedula por username
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const login = async () => {
  error.value = ''
  loading.value = true

  try {
    // El backend (SimpleJWT) espera 'username' por defecto
    const response = await api.post('/api/login/', {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('access', response.data.access)
    localStorage.setItem('refresh', response.data.refresh)

    router.push('/dashboard')
  } catch (err) {
    // Mensaje genérico para mayor seguridad
    error.value = 'Usuario o contraseña incorrecta'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <h2>Tenant Login</h2>

    <input
      v-model="username"
      placeholder="Nombre de usuario"
      type="text"
    />

    <input
      v-model="password"
      type="password"
      placeholder="Contraseña"
      @keyup.enter="login"
    />

    <button @click="login" :disabled="loading">
      {{ loading ? 'Ingresando...' : 'Ingresar' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<style scoped>
/* Tu estilo se mantiene igual */
.login {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-family: Arial, sans-serif;
}

input {
  margin: 10px;
  padding: 10px;
  width: 260px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

button {
  padding: 10px 20px;
  cursor: pointer;
  border: none;
  border-radius: 6px;
  background: #111827;
  color: white;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>