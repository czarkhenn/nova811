<template>
  <div class="modal fade" id="twoFactorSetupModal" tabindex="-1" aria-labelledby="twoFactorSetupModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="twoFactorSetupModalLabel">
            <i class="bi bi-shield-lock me-2"></i>
            Enable Two-Factor Authentication
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <!-- Step 1: Instructions -->
          <div v-if="currentStep === 1" class="text-center">
            <div class="mb-4">
              <i class="bi bi-shield-check display-1 text-success"></i>
            </div>
            <h4 class="mb-3">Secure Your Account</h4>
            <p class="text-muted mb-4">
              Two-factor authentication adds an extra layer of security to your account.
              Follow the steps below to set it up.
            </p>
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Demo Mode:</strong> For demonstration purposes, use the code <strong>"1234"</strong> to complete setup.
            </div>
            <button type="button" class="btn btn-primary" @click="nextStep">
              <i class="bi bi-arrow-right me-1"></i>
              Get Started
            </button>
          </div>

          <!-- Step 2: QR Code Display -->
          <div v-if="currentStep === 2" class="text-center">
            <h4 class="mb-3">Scan QR Code</h4>
            <p class="text-muted mb-4">
              Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
            </p>
            
            <!-- Mock QR Code -->
            <div class="mb-4">
              <div class="qr-code-container mx-auto">
                <img 
                  :src="setupData?.qr_code_url || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OTk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk1vY2sgUVIgQ29kZTwvdGV4dD48L3N2Zz4='"
                  alt="QR Code for 2FA Setup"
                  class="img-fluid border rounded"
                  style="max-width: 200px; max-height: 200px;"
                />
              </div>
            </div>

            <!-- Manual Entry Option -->
            <div class="alert alert-secondary">
              <small>
                <strong>Can't scan?</strong> Enter this code manually:<br>
                <code>{{ setupData?.secret_key || 'MOCK_SECRET_KEY_FOR_DEMO' }}</code>
              </small>
            </div>

            <div class="d-flex justify-content-between">
              <button type="button" class="btn btn-outline-secondary" @click="previousStep">
                <i class="bi bi-arrow-left me-1"></i>
                Back
              </button>
              <button type="button" class="btn btn-primary" @click="nextStep">
                <i class="bi bi-arrow-right me-1"></i>
                Next
              </button>
            </div>
          </div>

          <!-- Step 3: Verification -->
          <div v-if="currentStep === 3" class="text-center">
            <h4 class="mb-3">Verify Setup</h4>
            <p class="text-muted mb-4">
              Enter the 6-digit code from your authenticator app to complete setup.
            </p>

            <form @submit.prevent="verifyAndEnable">
              <div class="mb-3">
                <label for="verificationCode" class="form-label">Verification Code</label>
                <input
                  id="verificationCode"
                  v-model="verificationCode"
                  type="text"
                  class="form-control form-control-lg text-center"
                  :class="{ 'is-invalid': errors.verificationCode }"
                  placeholder="Enter 6-digit code"
                  maxlength="6"
                  required
                  style="font-size: 1.5rem; letter-spacing: 0.5rem;"
                />
                <div v-if="errors.verificationCode" class="invalid-feedback">
                  {{ errors.verificationCode }}
                </div>
                <div class="form-text">
                  <i class="bi bi-info-circle me-1"></i>
                  Demo: Use "1234" as the verification code
                </div>
              </div>

              <div class="d-flex justify-content-between">
                <button type="button" class="btn btn-outline-secondary" @click="previousStep">
                  <i class="bi bi-arrow-left me-1"></i>
                  Back
                </button>
                <button
                  type="submit"
                  class="btn btn-success"
                  :disabled="isLoading || !verificationCode"
                >
                  <span
                    v-if="isLoading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  <i v-else class="bi bi-check-lg me-1"></i>
                  {{ isLoading ? 'Enabling...' : 'Enable 2FA' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Step 4: Success -->
          <div v-if="currentStep === 4" class="text-center">
            <div class="mb-4">
              <i class="bi bi-check-circle-fill display-1 text-success"></i>
            </div>
            <h4 class="mb-3 text-success">2FA Enabled Successfully!</h4>
            <p class="text-muted mb-4">
              Your account is now protected with two-factor authentication.
            </p>
            
            <!-- Backup Codes -->
            <div class="alert alert-warning text-start">
              <h6><i class="bi bi-exclamation-triangle me-2"></i>Save Your Backup Codes</h6>
              <p class="mb-2">Store these backup codes in a safe place. You can use them to access your account if you lose your authenticator device:</p>
              <div class="backup-codes">
                <code v-for="code in setupData?.backup_codes" :key="code" class="d-block">{{ code }}</code>
              </div>
            </div>

            <button type="button" class="btn btn-primary" data-bs-dismiss="modal" @click="handleSuccess">
              <i class="bi bi-check-lg me-1"></i>
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { authService } from '@/services/auth.js'
import { useToast } from 'vue-toastification'

const emit = defineEmits(['success'])
const toast = useToast()

const currentStep = ref(1)
const isLoading = ref(false)
const verificationCode = ref('')
const setupData = ref(null)

const errors = reactive({
  verificationCode: '',
})

const nextStep = async () => {
  if (currentStep.value === 1) {
    // Load setup data when moving to step 2
    try {
      isLoading.value = true
      setupData.value = await authService.get2FASetup()
    } catch (error) {
      console.error('Failed to load 2FA setup data:', error)
      toast.error('Failed to load setup data. Please try again.')
      return
    } finally {
      isLoading.value = false
    }
  }
  
  if (currentStep.value < 4) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const verifyAndEnable = async () => {
  // Clear previous errors
  errors.verificationCode = ''

  if (!verificationCode.value) {
    errors.verificationCode = 'Verification code is required'
    return
  }

  try {
    isLoading.value = true
    
    // Enable 2FA with the verification code
    await authService.enable2FA(verificationCode.value)
    
    // Move to success step
    currentStep.value = 4
    
  } catch (error) {
    console.error('2FA enable error:', error)
    if (error.response?.data?.error) {
      errors.verificationCode = error.response.data.error
    } else {
      errors.verificationCode = 'Invalid verification code. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}

const handleSuccess = () => {
  // Reset modal state
  currentStep.value = 1
  verificationCode.value = ''
  errors.verificationCode = ''
  setupData.value = null
  
  // Emit success event to parent
  emit('success')
}

// Reset modal when it's opened
const resetModal = () => {
  currentStep.value = 1
  verificationCode.value = ''
  errors.verificationCode = ''
  setupData.value = null
}

// Expose reset method for parent component
defineExpose({
  resetModal
})
</script>

<style scoped>
.qr-code-container {
  max-width: 250px;
}

.backup-codes {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.backup-codes code {
  background-color: #f8f9fa;
  padding: 0.25rem 0.5rem;
  margin: 0.1rem 0;
  border-radius: 0.25rem;
}

.modal-dialog {
  display: flex;
  align-items: center;
  min-height: calc(100vh - 1rem);
}

.modal-body {
  min-height: 400px;
  padding: 2rem;
}

.form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

/* Ensure proper vertical centering for all screen sizes */
@media (min-width: 576px) {
  .modal-dialog {
    min-height: calc(100vh - 3.5rem);
  }
}
</style>
