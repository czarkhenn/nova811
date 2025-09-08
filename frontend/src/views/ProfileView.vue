<template>
  <AppLayout>
    <div class="profile">
      <div class="row">
        <div class="col-lg-8 mx-auto">
          <!-- Profile Header -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body text-center py-5">
              <div class="mb-3">
                <i class="bi bi-person-circle display-1 text-primary"></i>
              </div>
              <h2 class="mb-1">{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}</h2>
              <p class="text-muted mb-2">{{ authStore.user?.email }}</p>
              <span class="badge bg-primary">
                {{ authStore.user?.role === 'admin' ? 'Administrator' : 'Contractor' }}
              </span>
            </div>
          </div>

          <!-- Profile Information -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-person-gear me-2"></i>
                Profile Information
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="handleUpdateProfile">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="firstName" class="form-label">First Name</label>
                    <input
                      id="firstName"
                      v-model="profileForm.firstName"
                      type="text"
                      class="form-control"
                      :class="{ 'is-invalid': errors.firstName }"
                      required
                    />
                    <div v-if="errors.firstName" class="invalid-feedback">
                      {{ errors.firstName }}
                    </div>
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="lastName" class="form-label">Last Name</label>
                    <input
                      id="lastName"
                      v-model="profileForm.lastName"
                      type="text"
                      class="form-control"
                      :class="{ 'is-invalid': errors.lastName }"
                      required
                    />
                    <div v-if="errors.lastName" class="invalid-feedback">
                      {{ errors.lastName }}
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <input
                    id="email"
                    v-model="profileForm.email"
                    type="email"
                    class="form-control"
                    :class="{ 'is-invalid': errors.email }"
                    required
                  />
                  <div v-if="errors.email" class="invalid-feedback">
                    {{ errors.email }}
                  </div>
                </div>

                <div class="mb-3">
                  <label for="phoneNumber" class="form-label">Phone Number</label>
                  <input
                    id="phoneNumber"
                    v-model="profileForm.phoneNumber"
                    type="tel"
                    class="form-control"
                    :class="{ 'is-invalid': errors.phoneNumber }"
                  />
                  <div v-if="errors.phoneNumber" class="invalid-feedback">
                    {{ errors.phoneNumber }}
                  </div>
                </div>

                <div class="d-flex justify-content-between">
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="resetForm"
                  >
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Reset
                  </button>
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="authStore.isLoading"
                  >
                    <span
                      v-if="authStore.isLoading"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    <i v-else class="bi bi-check-lg me-1"></i>
                    {{ authStore.isLoading ? 'Updating...' : 'Update Profile' }}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Change Password -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-key me-2"></i>
                Change Password
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="handleChangePassword">
                <div class="mb-3">
                  <label for="currentPassword" class="form-label">Current Password</label>
                  <div class="input-group">
                    <input
                      id="currentPassword"
                      v-model="passwordForm.currentPassword"
                      :type="showCurrentPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.currentPassword }"
                      required
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showCurrentPassword = !showCurrentPassword"
                    >
                      <i :class="showCurrentPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.currentPassword" class="invalid-feedback">
                      {{ errors.currentPassword }}
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="newPassword" class="form-label">New Password</label>
                  <div class="input-group">
                    <input
                      id="newPassword"
                      v-model="passwordForm.newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.newPassword }"
                      required
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showNewPassword = !showNewPassword"
                    >
                      <i :class="showNewPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.newPassword" class="invalid-feedback">
                      {{ errors.newPassword }}
                    </div>
                  </div>
                  <div class="form-text">
                    Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.
                  </div>
                </div>

                <div class="mb-3">
                  <label for="confirmNewPassword" class="form-label">Confirm New Password</label>
                  <div class="input-group">
                    <input
                      id="confirmNewPassword"
                      v-model="passwordForm.confirmNewPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.confirmNewPassword }"
                      required
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.confirmNewPassword" class="invalid-feedback">
                      {{ errors.confirmNewPassword }}
                    </div>
                  </div>
                </div>

                <div class="d-flex justify-content-between">
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="resetPasswordForm"
                  >
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Reset
                  </button>
                  <button
                    type="submit"
                    class="btn btn-warning"
                    :disabled="authStore.isLoading"
                  >
                    <span
                      v-if="authStore.isLoading"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    <i v-else class="bi bi-key me-1"></i>
                    {{ authStore.isLoading ? 'Changing...' : 'Change Password' }}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- Two-Factor Authentication -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-shield-lock me-2"></i>
                Two-Factor Authentication
              </h5>
            </div>
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-8">
                  <div class="d-flex align-items-center mb-2">
                    <i 
                      :class="authStore.user?.two_factor_enabled ? 'bi bi-shield-check text-success' : 'bi bi-shield-x text-warning'"
                      class="me-2"
                      style="font-size: 1.2rem;"
                    ></i>
                    <strong>Status:</strong>
                    <span 
                      class="ms-2 badge"
                      :class="authStore.user?.two_factor_enabled ? 'bg-success' : 'bg-warning'"
                    >
                      {{ authStore.user?.two_factor_enabled ? 'Enabled' : 'Disabled' }}
                    </span>
                  </div>
                  <p class="text-muted mb-0">
                    {{ authStore.user?.two_factor_enabled 
                      ? 'Your account is protected with two-factor authentication.' 
                      : 'Add an extra layer of security to your account.' 
                    }}
                  </p>
                </div>
                <div class="col-md-4 text-end">
                  <button
                    v-if="!authStore.user?.two_factor_enabled"
                    type="button"
                    class="btn btn-success"
                    data-bs-toggle="modal"
                    data-bs-target="#twoFactorSetupModal"
                    @click="resetSetupModal"
                  >
                    <i class="bi bi-shield-plus me-1"></i>
                    Enable 2FA
                  </button>
                  <button
                    v-else
                    type="button"
                    class="btn btn-outline-danger"
                    @click="handleDisable2FA"
                    :disabled="isDisabling2FA"
                  >
                    <span
                      v-if="isDisabling2FA"
                      class="spinner-border spinner-border-sm me-2"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    <i v-else class="bi bi-shield-minus me-1"></i>
                    {{ isDisabling2FA ? 'Disabling...' : 'Disable 2FA' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Information -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-info-circle me-2"></i>
                Account Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <strong>Account Status:</strong>
                  <span class="ms-2 badge bg-success">Active</span>
                </div>
                <div class="col-md-6 mb-3">
                  <strong>Member Since:</strong>
                  <span class="ms-2">{{ formatDate(authStore.user?.date_joined) }}</span>
                </div>
                <div class="col-md-6 mb-3">
                  <strong>Last Login:</strong>
                  <span class="ms-2">{{ formatDate(authStore.user?.last_login) }}</span>
                </div>
                <div class="col-md-6 mb-3">
                  <strong>User ID:</strong>
                  <span class="ms-2">{{ authStore.user?.id }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Two-Factor Setup Modal -->
    <TwoFactorSetup @success="handle2FASuccess" ref="twoFactorSetupRef" />
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useToast } from 'vue-toastification'
import AppLayout from '@/components/AppLayout.vue'
import TwoFactorSetup from '@/components/TwoFactorSetup.vue'
import { authService } from '@/services/auth.js'

const authStore = useAuthStore()
const toast = useToast()

// 2FA related refs
const twoFactorSetupRef = ref(null)
const isDisabling2FA = ref(false)

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const profileForm = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phoneNumber: '',
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: '',
})

const errors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phoneNumber: '',
  currentPassword: '',
  newPassword: '',
  confirmNewPassword: '',
})

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const resetForm = () => {
  if (authStore.user) {
    profileForm.firstName = authStore.user.first_name || ''
    profileForm.lastName = authStore.user.last_name || ''
    profileForm.email = authStore.user.email || ''
    profileForm.phoneNumber = authStore.user.phone_number || ''
  }
  
  // Clear errors
  Object.keys(errors).forEach(key => {
    if (key !== 'currentPassword' && key !== 'newPassword' && key !== 'confirmNewPassword') {
      errors[key] = ''
    }
  })
}

const resetPasswordForm = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmNewPassword = ''
  
  // Clear password errors
  errors.currentPassword = ''
  errors.newPassword = ''
  errors.confirmNewPassword = ''
}

const validateProfileForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    if (key !== 'currentPassword' && key !== 'newPassword' && key !== 'confirmNewPassword') {
      errors[key] = ''
    }
  })

  let isValid = true

  if (!profileForm.firstName.trim()) {
    errors.firstName = 'First name is required'
    isValid = false
  }

  if (!profileForm.lastName.trim()) {
    errors.lastName = 'Last name is required'
    isValid = false
  }

  if (!profileForm.email) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileForm.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (profileForm.phoneNumber && !/^[\+]?[1-9][\d]{0,15}$/.test(profileForm.phoneNumber.replace(/\s/g, ''))) {
    errors.phoneNumber = 'Please enter a valid phone number'
    isValid = false
  }

  return isValid
}

const validatePasswordForm = () => {
  // Reset password errors
  errors.currentPassword = ''
  errors.newPassword = ''
  errors.confirmNewPassword = ''

  let isValid = true

  if (!passwordForm.currentPassword) {
    errors.currentPassword = 'Current password is required'
    isValid = false
  }

  if (!passwordForm.newPassword) {
    errors.newPassword = 'New password is required'
    isValid = false
  } else if (passwordForm.newPassword.length < 8) {
    errors.newPassword = 'Password must be at least 8 characters long'
    isValid = false
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(passwordForm.newPassword)) {
    errors.newPassword = 'Password must contain uppercase, lowercase, and numbers'
    isValid = false
  }

  if (!passwordForm.confirmNewPassword) {
    errors.confirmNewPassword = 'Please confirm your new password'
    isValid = false
  } else if (passwordForm.newPassword !== passwordForm.confirmNewPassword) {
    errors.confirmNewPassword = 'Passwords do not match'
    isValid = false
  }

  return isValid
}

const handleUpdateProfile = async () => {
  if (!validateProfileForm()) return

  try {
    await authStore.updateProfile({
      first_name: profileForm.firstName.trim(),
      last_name: profileForm.lastName.trim(),
      email: profileForm.email.trim(),
      phone_number: profileForm.phoneNumber.trim(),
    })

    toast.success('Profile updated successfully!')
  } catch (error) {
    console.error('Profile update error:', error)
    toast.error('Failed to update profile. Please try again.')
  }
}

const handleChangePassword = async () => {
  if (!validatePasswordForm()) return

  try {
    await authStore.changePassword(passwordForm.currentPassword, passwordForm.newPassword)
    toast.success('Password changed successfully!')
    resetPasswordForm()
  } catch (error) {
    console.error('Password change error:', error)
    toast.error('Failed to change password. Please check your current password.')
  }
}

// 2FA Handler Functions
const resetSetupModal = () => {
  if (twoFactorSetupRef.value) {
    twoFactorSetupRef.value.resetModal()
  }
}

const handle2FASuccess = async () => {
  try {
    // Refresh user data to get updated 2FA status
    await authStore.fetchUser()
    toast.success('Two-factor authentication enabled successfully!')
  } catch (error) {
    console.error('Failed to refresh user data:', error)
    // Still show success since 2FA was enabled
    toast.success('Two-factor authentication enabled successfully!')
  }
}

const handleDisable2FA = async () => {
  if (!confirm('Are you sure you want to disable two-factor authentication? This will make your account less secure.')) {
    return
  }

  try {
    isDisabling2FA.value = true
    await authService.disable2FA()
    
    // Refresh user data to get updated 2FA status
    await authStore.fetchUser()
    toast.success('Two-factor authentication disabled successfully!')
  } catch (error) {
    console.error('2FA disable error:', error)
    toast.error('Failed to disable two-factor authentication. Please try again.')
  } finally {
    isDisabling2FA.value = false
  }
}

onMounted(async () => {
  // Ensure user data is loaded
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('Failed to fetch user data:', error)
    }
  }
  
  resetForm()
})
</script>

<style scoped>
.profile {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}
</style>
