import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const expiresAt = ref<number | null>(
    localStorage.getItem('expiresAt') ? parseInt(localStorage.getItem('expiresAt')!) : null
  )

  const isAuthenticated = computed(() => {
    if (!token.value || !expiresAt.value) return false
    return Date.now() < expiresAt.value
  })

  async function login(password: string): Promise<boolean> {
    try {
      const response = await api.post('/auth/login', { password })
      const { access_token, expires_in } = response.data

      token.value = access_token
      expiresAt.value = Date.now() + expires_in * 1000

      localStorage.setItem('token', access_token)
      localStorage.setItem('expiresAt', expiresAt.value.toString())

      return true
    } catch {
      return false
    }
  }

  function logout() {
    token.value = null
    expiresAt.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('expiresAt')
  }

  return {
    token,
    expiresAt,
    isAuthenticated,
    login,
    logout,
  }
})
