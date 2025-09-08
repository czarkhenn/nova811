<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header border-0 pb-0">
          <h5 class="modal-title">
            <i class="bi bi-shield-check text-primary me-2"></i>
            Two-Factor Authentication
          </h5>
        </div>
        
        <div class="modal-body px-4 py-3">
          <div class="text-center mb-4">
            <div class="alert alert-info border-0" style="background-color: #e3f2fd;">
              <i class="bi bi-envelope me-2"></i>
              <div>
                <strong>Verification code sent to:</strong><br>
                <span class="fw-bold">{{ authStore.twoFactorData.maskedEmail }}</span>
              </div>
              <div class="mt-2">
                <span v-if="authStore.twoFactorData.userRequires2FA">
                  Enter your 2FA verification code to complete login
                </span>
                <span v-else>
                  Enter verification code or skip to continue
                </span>
              </div>
            </div>
          </div>

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
                placeholder="Enter 6-digit code"
                maxlength="6"
                @input="clearError"
                @keyup.enter="handleVerify"
                :disabled="isLoading"
              />
            </div>
            <div v-if="hasError" class="invalid-feedback d-block">
              {{ errorMessage }}
            </div>
          </div>

          <div class="d-flex gap-2">
            <button
              type="button"
              class="btn btn-primary flex-fill"
              @click="handleVerify"
              :disabled="isLoading || !verificationCode.trim()"
            >
              <span
                v-if="isLoading && !isSkipping"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ isLoading && !isSkipping ? 'Verifying...' : 'Verify Code' }}
            </button>
            
            <button
              v-if="!authStore.twoFactorData.userRequires2FA"
              type="button"
              class="btn btn-outline-secondary"
              @click="handleSkip"
              :disabled="isLoading"
            >
              <span
                v-if="isLoading && isSkipping"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ isLoading && isSkipping ? 'Skipping...' : 'Skip' }}
            </button>
          </div>

          <div class="text-center mt-3">
            <small class="text-muted">
              <i class="bi bi-question-circle me-1"></i>
              Having trouble? Contact support for assistance.
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const verificationCode = ref('')
const isLoading = ref(false)
const isSkipping = ref(false)
const hasError = ref(false)
const errorMessage = ref('')

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

  clearError()
  isLoading.value = true
  isSkipping.value = false

  try {
    // Use the auth store's smart login verify method
    await authStore.smartLoginVerify(verificationCode.value.trim(), false)
    
    // If we reach here, login was successful (no exception thrown)
    toast.success('Login successful!')
    router.replace('/dashboard')
  } catch (error) {
    showError(authStore.twoFactorError || 'Verification failed. Please try again.')
  } finally {
    isLoading.value = false
    isSkipping.value = false
  }
}

const handleSkip = async () => {
  if (authStore.twoFactorData.userRequires2FA) {
    showError('2FA is required for your account')
    return
  }

  clearError()
  isLoading.value = true
  isSkipping.value = true

  try {
    // Use the auth store's smart login verify method with skip=true
    await authStore.smartLoginVerify('', true)
    
    // If we reach here, login was successful (no exception thrown)
    toast.success('Login successful!')
    router.replace('/dashboard')
  } catch (error) {
    showError(authStore.twoFactorError || 'Skip failed. Please try again.')
  } finally {
    isLoading.value = false
    isSkipping.value = false
  }
}

onMounted(() => {
  const input = document.getElementById('verificationCode')
  if (input) {
    input.focus()
  }
})

defineExpose({
  showError,
  clearError,
})
</script>

<style scoped>
.modal {
  backdrop-filter: blur(3px);
}

.modal-content {
  border: none;
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 1rem 1rem 0 0;
}

.modal-title {
  font-weight: 600;
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

.modal.show {
  animation: modalFadeIn 0.3s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
