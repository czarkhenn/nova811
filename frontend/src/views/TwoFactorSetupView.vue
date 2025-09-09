<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <i class="bi bi-shield-check fs-1 text-primary"></i>
                <h2 class="mt-2">Two-Factor Authentication</h2>
                <p class="text-muted">Secure your account with an additional layer of protection.</p>
              </div>

              <!-- User Message -->
              <div class="text-center mb-4">
                <div 
                  class="alert border-0" 
                  :class="isTwoFactorEnabled ? 'alert-success' : 'alert-info'"
                  :style="isTwoFactorEnabled ? 'background-color: #d1e7dd;' : 'background-color: #e3f2fd;'"
                >
                  <i 
                    class="me-2" 
                    :class="isTwoFactorEnabled ? 'bi bi-check-circle-fill text-success' : 'bi bi-info-circle'"
                  ></i>
                  <div>
                    <strong>{{ isTwoFactorEnabled ? 'Great!' : 'Welcome!' }}</strong><br>
                    <span class="text-muted">
                      {{ isTwoFactorEnabled 
                        ? 'Two-factor authentication is already enabled for your account.' 
                        : 'You can enable two-factor authentication for enhanced security, or skip this step for now.' 
                      }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Verification Code Input -->
              <div class="mb-4">
                <label for="verificationCode" class="form-label fw-semibold">
                  Verification Code
                </label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0">
                    <i class="bi bi-key"></i>
                  </span>
                  <input
                    id="verificationCode"
                    v-model="verificationCode"
                    type="text"
                    class="form-control border-start-0 ps-0"
                    :class="{ 'is-invalid': hasError }"
                    placeholder="Enter 4-digit code"
                    maxlength="4"
                    @input="clearError"
                    @keyup.enter="handleVerify"
                    :disabled="isLoading"
                  />
                </div>
                <div v-if="hasError" class="invalid-feedback d-block">
                  {{ errorMessage }}
                </div>
                <small class="text-muted">
                  For demo purposes, use code: <strong>1234</strong> to enable 2FA
                </small>
              </div>

              <!-- Action Buttons -->
              <div class="d-flex gap-2 mb-3">
                <button
                  type="button"
                  class="btn btn-primary flex-fill"
                  @click="handleVerify"
                  :disabled="isEnableButtonDisabled"
                >
                  <span
                    v-if="isLoading && !isSkipping"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ enableButtonText }}
                </button>
                
                <button
                  type="button"
                  class="btn btn-outline-secondary flex-fill"
                  @click="handleSkip"
                  :disabled="isLoading"
                >
                  <span
                    v-if="isLoading && isSkipping"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ isLoading && isSkipping ? 'Continuing...' : 'Skip for Now' }}
                </button>
              </div>

              <!-- Help Text -->
              <div class="text-center">
                <small class="text-muted">
                  <i class="bi bi-info-circle me-1"></i>
                  You can always enable 2FA later from your profile settings.
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const verificationCode = ref('')
const isLoading = ref(false)
const isSkipping = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

// Computed properties
const isTwoFactorEnabled = computed(() => {
  return authStore.user?.two_factor_enabled === true
})

const enableButtonText = computed(() => {
  if (isTwoFactorEnabled.value) {
    return isLoading.value && !isSkipping.value ? 'Verifying...' : 'Verify'
  }
  return isLoading.value && !isSkipping.value ? 'Enabling 2FA...' : 'Enable 2FA'
})

const isEnableButtonDisabled = computed(() => {
  return isLoading.value || !verificationCode.value.trim()
})

// Methods
const clearError = () => {
  hasError.value = false
  errorMessage.value = ''
}

const showError = (message) => {
  hasError.value = true
  errorMessage.value = message
  isLoading.value = false
  isSkipping.value = false
}

const handleVerify = async () => {
  if (!verificationCode.value.trim()) {
    showError('Please enter a verification code')
    return
  }

  if (verificationCode.value.length !== 4) {
    showError('Verification code must be 4 digits')
    return
  }

  if (verificationCode.value !== '1234') {
    showError('Invalid verification code. Use 1234 for demo.')
    return
  }

  clearError()
  isLoading.value = true
  isSkipping.value = false

  try {
    // First verify user (fetch user data)
    await authStore.verifyUser()
    
    // Then enable 2FA for the user
    await authStore.enable2FA(verificationCode.value.trim())
    
    toast.success('Two-factor authentication enabled successfully!')
    router.replace('/dashboard')
  } catch (error) {
    console.error('2FA enable error:', error)
    showError('Failed to enable 2FA. Please try again.')
  } finally {
    isLoading.value = false
    isSkipping.value = false
  }
}

const handleSkip = async () => {
  clearError()
  isLoading.value = true
  isSkipping.value = true

  try {
    await authStore.verifyUser()
    
    toast.info('2FA setup skipped. You can enable it later from your profile.')
    router.replace('/dashboard')
  } catch (error) {
    console.error('Skip error:', error)
    showError('Something went wrong. Please try again.')
  } finally {
    isLoading.value = false
    isSkipping.value = false
  }
}

// Initialize component on mount
onMounted(async () => {
  // Ensure we have the latest user data to check 2FA status
  try {
    if (authStore.isAuthenticated && !authStore.user) {
      await authStore.verifyUser()
    }
  } catch (error) {
    console.error('Failed to fetch user data:', error)
    // Continue with component initialization even if user fetch fails
  }

  // Focus input on mount (only if 2FA is not already enabled)
  const input = document.getElementById('verificationCode')
  if (input && !isTwoFactorEnabled.value) {
    input.focus()
  }
})
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 1rem;
}

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.form-control {
  border-left: none;
}

.form-control:focus {
  box-shadow: none;
  border-color: #86b7fe;
}

.btn {
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-weight: 500;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
  transform: translateY(-1px);
}

.btn-outline-secondary {
  border-color: #dee2e6;
  color: #6c757d;
}

.btn-outline-secondary:hover {
  background-color: #f8f9fa;
  border-color: #dee2e6;
  color: #495057;
}

.alert-info {
  color: #0c5460;
}

.invalid-feedback {
  font-size: 0.875rem;
}

.text-muted {
  color: #6c757d !important;
}
</style>
