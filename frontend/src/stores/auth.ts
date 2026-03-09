import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
import api from '@/services/api'

export interface AuthUser {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: 'admin' | 'manager' | 'employee' | 'client'
  phone: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const token = ref(localStorage.getItem('access_token') || '')

  const isAuthenticated = computed(() => !!token.value)
  const fullName = computed(() =>
    user.value ? `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.username : '',
  )

  async function login(username: string, password: string) {
    const { data } = await axios.post('/api/login/', { username, password })
    token.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchUser()
  }

  async function fetchUser() {
    try {
      const { data } = await api.get('/users/me/')
      user.value = data
    } catch {
      // silencioso
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  // Restaurar sesión al iniciar la app
  if (token.value) fetchUser()

  return { user, token, isAuthenticated, fullName, login, logout, fetchUser }
})
