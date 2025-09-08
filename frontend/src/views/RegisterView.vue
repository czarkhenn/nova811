<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <i class="bi bi-person-plus fs-1 text-primary"></i>
                <h2 class="mt-2">Create Account</h2>
                <p class="text-muted">Join us today! Please fill in your information to get started.</p>
              </div>

              <form @submit.prevent="handleRegister">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="firstName" class="form-label">First Name</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-person"></i>
                      </span>
                      <input
                        id="firstName"
                        v-model="form.firstName"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.firstName }"
                        placeholder="Enter your first name"
                        required
                      />
                      <div v-if="errors.firstName" class="invalid-feedback">
                        {{ errors.firstName }}
                      </div>
                    </div>
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="lastName" class="form-label">Last Name</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-person"></i>
                      </span>
                      <input
                        id="lastName"
                        v-model="form.lastName"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.lastName }"
                        placeholder="Enter your last name"
                        required
                      />
                      <div v-if="errors.lastName" class="invalid-feedback">
                        {{ errors.lastName }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-at"></i>
                    </span>
                    <input
                      id="username"
                      v-model="form.username"
                      type="text"
                      class="form-control"
                      :class="{ 'is-invalid': errors.username }"
                      placeholder="Choose a username"
                      required
                    />
                    <div v-if="errors.username" class="invalid-feedback">
                      {{ errors.username }}
                    </div>
                  </div>
                  <div class="form-text">
                    Username must be 3-30 characters long and contain only letters, numbers, and underscores.
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input
                      id="email"
                      v-model="form.email"
                      type="email"
                      class="form-control"
                      :class="{ 'is-invalid': errors.email }"
                      placeholder="Enter your email"
                      required
                    />
                    <div v-if="errors.email" class="invalid-feedback">
                      {{ errors.email }}
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="phoneNumber" class="form-label">Phone Number <span class="text-muted">(Optional)</span></label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-telephone"></i>
                    </span>
                    <input
                      id="phoneNumber"
                      v-model="form.phoneNumber"
                      type="tel"
                      class="form-control"
                      :class="{ 'is-invalid': errors.phoneNumber }"
                      placeholder="Enter your phone number"
                    />
                    <div v-if="errors.phoneNumber" class="invalid-feedback">
                      {{ errors.phoneNumber }}
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="role" class="form-label">Role</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-shield-check"></i>
                    </span>
                    <select
                      id="role"
                      v-model="form.role"
                      class="form-select"
                      :class="{ 'is-invalid': errors.role }"
                      required
                    >
                      <option value="contractor">Contractor</option>
                      <option value="admin">Admin</option>
                    </select>
                    <div v-if="errors.role" class="invalid-feedback">
                      {{ errors.role }}
                    </div>
                  </div>
                  <div class="form-text">
                    Select your role. Contractors have standard access, while Admins have full system access.
                  </div>
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input
                      id="password"
                      v-model="form.password"
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.password }"
                      placeholder="Enter your password"
                      required
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showPassword = !showPassword"
                    >
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.password" class="invalid-feedback">
                      {{ errors.password }}
                    </div>
                  </div>
                  <div class="form-text">
                    Password must be at least 8 characters long and contain uppercase, lowercase, and numbers.
                  </div>
                </div>

                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock-fill"></i>
                    </span>
                    <input
                      id="confirmPassword"
                      v-model="form.confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      class="form-control"
                      :class="{ 'is-invalid': errors.confirmPassword }"
                      placeholder="Confirm your password"
                      required
                    />
                    <button
                      type="button"
                      class="btn btn-outline-secondary"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="errors.confirmPassword" class="invalid-feedback">
                      {{ errors.confirmPassword }}
                    </div>
                  </div>
                </div>

                <div class="mb-3 form-check">
                  <input
                    id="terms"
                    v-model="form.acceptTerms"
                    type="checkbox"
                    class="form-check-input"
                    :class="{ 'is-invalid': errors.acceptTerms }"
                    required
                  />
                  <label for="terms" class="form-check-label">
                    I agree to the <a href="#" class="text-decoration-none">Terms of Service</a> and 
                    <a href="#" class="text-decoration-none">Privacy Policy</a>
                  </label>
                  <div v-if="errors.acceptTerms" class="invalid-feedback">
                    {{ errors.acceptTerms }}
                  </div>
                </div>

                <div v-if="authStore.error" class="alert alert-danger" role="alert">
                  <i class="bi bi-exclamation-triangle me-2"></i>
                  <div v-if="typeof authStore.error === 'string'">
                    {{ authStore.error }}
                  </div>
                  <div v-else>
                    <div v-for="(errorList, field) in authStore.error" :key="field">
                      <strong>{{ field }}:</strong>
                      <ul class="mb-0">
                        <li v-for="error in errorList" :key="error">{{ error }}</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-3"
                  :disabled="authStore.isLoading"
                >
                  <span
                    v-if="authStore.isLoading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ authStore.isLoading ? 'Creating Account...' : 'Create Account' }}
                </button>

                <div class="text-center">
                  <p class="mb-0">
                    Already have an account?
                    <router-link to="/login" class="text-decoration-none">
                      Sign in here
                    </router-link>
                  </p>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  firstName: '',
  lastName: '',
  username: '',
  email: '',
  phoneNumber: '',
  role: 'contractor',
  password: '',
  confirmPassword: '',
  acceptTerms: false,
})

const errors = reactive({
  firstName: '',
  lastName: '',
  username: '',
  email: '',
  phoneNumber: '',
  role: '',
  password: '',
  confirmPassword: '',
  acceptTerms: '',
})

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })

  let isValid = true

  // First name validation
  if (!form.firstName.trim()) {
    errors.firstName = 'First name is required'
    isValid = false
  }

  // Last name validation
  if (!form.lastName.trim()) {
    errors.lastName = 'Last name is required'
    isValid = false
  }

  // Username validation
  if (!form.username.trim()) {
    errors.username = 'Username is required'
    isValid = false
  } else if (form.username.length < 3) {
    errors.username = 'Username must be at least 3 characters long'
    isValid = false
  } else if (form.username.length > 30) {
    errors.username = 'Username must be no more than 30 characters long'
    isValid = false
  } else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) {
    errors.username = 'Username can only contain letters, numbers, and underscores'
    isValid = false
  }

  // Email validation
  if (!form.email) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  // Phone number validation (optional but if provided, should be valid)
  if (form.phoneNumber && !/^[\+]?[1-9][\d]{0,15}$/.test(form.phoneNumber.replace(/\s/g, ''))) {
    errors.phoneNumber = 'Please enter a valid phone number'
    isValid = false
  }

  // Password validation
  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters long'
    isValid = false
  } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(form.password)) {
    errors.password = 'Password must contain uppercase, lowercase, and numbers'
    isValid = false
  }

  // Confirm password validation
  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    isValid = false
  }

  // Terms acceptance validation
  if (!form.acceptTerms) {
    errors.acceptTerms = 'You must accept the terms and conditions'
    isValid = false
  }

  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return

  authStore.clearError()

  try {
    await authStore.register({
      firstName: form.firstName.trim(),
      lastName: form.lastName.trim(),
      username: form.username.trim(),
      email: form.email.trim(),
      phoneNumber: form.phoneNumber.trim(),
      role: form.role,
      password: form.password,
      confirmPassword: form.confirmPassword,
    })

    toast.success('Registration successful! Please check your email to activate your account.')
    router.push('/login')
  } catch (error) {
    console.error('Registration error:', error)
    toast.error('Registration failed. Please check your information and try again.')
  }
}

onMounted(() => {
  authStore.clearError()
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

.btn-primary {
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.form-text {
  font-size: 0.875rem;
}
</style>
