import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authService } from '@/services/auth.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const isInitialized = ref(false)
  const initPromise = ref(null)
  
  const tokenExists = ref(!!localStorage.getItem('access_token'))


  const isAuthenticated = computed(() => {
    const tokenValid = tokenExists.value && isTokenValid()
    const serviceAuth = authService.isAuthenticated()
    return tokenValid && serviceAuth
  })

  const isVerified = computed(() => {
    const hasValidToken = tokenExists.value && isTokenValid() && authService.isAuthenticated()
    const hasUserData = !!user.value
    return hasValidToken && hasUserData
  })

  const isAdmin = computed(() => {
    return user.value?.role === 'admin'
  })

  const isContractor = computed(() => {
    return user.value?.role === 'contractor'
  })

  function isTokenValid() {
    const token = localStorage.getItem('access_token')
    if (!token) return false

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Math.floor(Date.now() / 1000)
      
      return payload.exp && payload.exp > (currentTime + 30)
    } catch (error) {
      return false
    }
  }

  function loadPersistedUser() {
    try {
      const userData = localStorage.getItem('user_data')
      if (userData) {
        user.value = JSON.parse(userData)
      }
    } catch (error) {
      localStorage.removeItem('user_data')
    }
  }

  function persistUser(userData) {
    try {
      localStorage.setItem('user_data', JSON.stringify(userData))
      user.value = userData
    } catch (error) {
      // Silently handle error
    }
  }

  async function initAuth() {
    if (initPromise.value) {
      return initPromise.value
    }

    if (isInitialized.value) {
      return Promise.resolve()
    }

    initPromise.value = (async () => {
      isLoading.value = true
      
      try {
        loadPersistedUser()

        tokenExists.value = !!localStorage.getItem('access_token')

        const hasValidToken = isTokenValid() && authService.isAuthenticated()
        
        if (!hasValidToken) {
          if (localStorage.getItem('access_token')) {
            authService.logout()
            localStorage.removeItem('user_data')
            user.value = null
            error.value = null
            tokenExists.value = false
          }
        }
      } catch (error) {
        authService.logout()
        localStorage.removeItem('user_data')
        user.value = null
        error.value = null
        tokenExists.value = false
      } finally {
        isLoading.value = false
        isInitialized.value = true
        initPromise.value = null
      }
    })()

    return initPromise.value
  }

  async function login(email, password) {
    isLoading.value = true
    error.value = null

    try {
      await authService.login(email, password)
      tokenExists.value = !!localStorage.getItem('access_token')
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function verifyUser() {
    isLoading.value = true
    error.value = null

    try {
      await fetchUser()
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'User verification failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function register(userData) {
    isLoading.value = true
    error.value = null

    try {
      await authService.register(userData)
      return true
    } catch (err) {
      error.value = err.response?.data || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    try {
      const userData = await authService.getCurrentUser()
      persistUser(userData)
    } catch (err) {
      throw err
    }
  }

  function logout() {
    authService.logout()
    localStorage.removeItem('user_data')
    user.value = null
    error.value = null
    isInitialized.value = false
    tokenExists.value = false
  }

  async function updateProfile(profileData) {
    isLoading.value = true
    error.value = null

    try {
      const updatedUser = await authService.updateProfile(profileData)
      const mergedUser = { ...user.value, ...updatedUser }
      persistUser(mergedUser)
      return updatedUser
    } catch (err) {
      error.value = err.response?.data || 'Profile update failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function changePassword(currentPassword, newPassword) {
    isLoading.value = true
    error.value = null

    try {
      await authService.changePassword(currentPassword, newPassword)
      return true
    } catch (err) {
      error.value = err.response?.data || 'Password change failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  async function enable2FA(verificationCode) {
    isLoading.value = true
    error.value = null

    try {
      await authService.enable2FA(verificationCode)
      
      if (user.value) {
        user.value.two_factor_enabled = true
        persistUser(user.value)
      }
      
      return true
    } catch (err) {
      error.value = err.response?.data?.error || '2FA enable failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    user,
    isLoading,
    error,
    isAuthenticated,
    isVerified,
    isAdmin,
    isContractor,
    initAuth,
    login,
    verifyUser,
    register,
    fetchUser,
    logout,
    updateProfile,
    changePassword,
    clearError,
    enable2FA,
  }
})
