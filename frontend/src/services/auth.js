import api from './api.js'

export const authService = {
  // Smart login - first step (email/password validation)
  async smartLogin(email, password) {
    try {
      const response = await api.post('/users/smart-login/', {
        email,
        password,
      })
      
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Smart login verification - second step (2FA verification)
  async smartLoginVerify(tempSessionId, code, skip = false) {
    try {
      const response = await api.post('/users/smart-login/verify/', {
        temp_session_id: tempSessionId,
        code,
        skip,
      })
      
      const { access, refresh, user } = response.data
      
      // Store tokens
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      // Store user data if provided
      if (user) {
        localStorage.setItem('user_data', JSON.stringify(user))
      }
      
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Legacy login method (for backward compatibility)
  async login(email, password) {
    try {
      const response = await api.post('/auth/jwt/create/', {
        email,
        password,
      })
      
      const { access, refresh } = response.data
      
      // Store tokens
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
      
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Register user
  async register(userData) {
    try {
      const response = await api.post('/auth/users/', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        re_password: userData.confirmPassword,
        first_name: userData.firstName,
        last_name: userData.lastName,
        phone_number: userData.phoneNumber || '',
        role: userData.role,
      })
      
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get current user
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/users/me/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Logout user
  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
  },

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },

  // Refresh token
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        throw new Error('No refresh token available')
      }

      const response = await api.post('/auth/jwt/refresh/', {
        refresh: refreshToken,
      })

      const { access } = response.data
      localStorage.setItem('access_token', access)
      
      return access
    } catch (error) {
      this.logout()
      throw error
    }
  },

  // Change password using Djoser's standard endpoint
  async changePassword(currentPassword, newPassword) {
    try {
      const response = await api.post('/auth/users/set_password/', {
        current_password: currentPassword,
        new_password: newPassword,
        re_new_password: newPassword,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Update user profile
  async updateProfile(profileData) {
    try {
      const response = await api.patch('/auth/users/me/', profileData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Two-Factor Authentication methods
  
  // Get 2FA setup data
  async get2FASetup() {
    try {
      const response = await api.get('/users/two-factor/setup/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Enable 2FA with verification code
  async enable2FA(verificationCode) {
    try {
      const response = await api.post('/users/two-factor/enable/', {
        code: verificationCode,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Disable 2FA
  async disable2FA() {
    try {
      const response = await api.post('/users/two-factor/disable/')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Verify 2FA code
  async verify2FA(verificationCode) {
    try {
      const response = await api.post('/users/two-factor/verify/', {
        code: verificationCode,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Get 2FA status
  async get2FAStatus() {
    try {
      const response = await api.get('/users/two-factor/status/')
      return response.data
    } catch (error) {
      throw error
    }
  },
}
