import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAdminStore = defineStore('admin', () => {
  const token = ref(localStorage.getItem('admin_token') || '')

  const isAuthenticated = computed(() => !!token.value)

  async function login(key: string) {
    const { data } = await axios.post('/api/admin/login/', { key })
    token.value = data.token
    localStorage.setItem('admin_token', data.token)
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('admin_token')
  }

  return { token, isAuthenticated, login, logout }
})
