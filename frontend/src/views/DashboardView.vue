<template>
  <AppLayout>
    <div class="dashboard">
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 bg-primary text-white">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col">
                  <h1 class="h3 mb-1">
                    Welcome back, {{ authStore.user?.first_name }}!
                  </h1>
                  <p class="mb-0 opacity-75">
                    Here's what's happening with your account today.
                  </p>
                </div>
                <div class="col-auto">
                  <i class="bi bi-person-workspace display-4 opacity-50"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-primary mb-2">
                <i class="bi bi-person-check display-4"></i>
              </div>
              <h5 class="card-title">Profile Status</h5>
              <p class="card-text text-success">
                <i class="bi bi-check-circle me-1"></i>
                Active
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-info mb-2">
                <i class="bi bi-shield-lock display-4"></i>
              </div>
              <h5 class="card-title">Security</h5>
              <p class="card-text">
                <span :class="authStore.user?.two_factor_enabled ? 'text-success' : 'text-warning'">
                  <i :class="authStore.user?.two_factor_enabled ? 'bi bi-check-circle' : 'bi bi-exclamation-triangle'" class="me-1"></i>
                  {{ authStore.user?.two_factor_enabled ? '2FA Enabled' : '2FA Disabled' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-warning mb-2">
                <i class="bi bi-person-badge display-4"></i>
              </div>
              <h5 class="card-title">Role</h5>
              <p class="card-text">
                <span class="badge bg-primary">
                  {{ authStore.user?.role === 'admin' ? 'Administrator' : 'Contractor' }}
                </span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-success mb-2">
                <i class="bi bi-calendar-check display-4"></i>
              </div>
              <h5 class="card-title">Last Login</h5>
              <p class="card-text text-muted">
                {{ formatDate(authStore.user?.last_login) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-lightning me-2"></i>
                Quick Actions
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <router-link to="/profile" class="btn btn-outline-primary w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i class="bi bi-person-gear display-6 mb-2"></i>
                    <span>Update Profile</span>
                  </router-link>
                </div>
                <div class="col-md-4 mb-3">
                  <router-link to="/profile" class="btn btn-outline-info w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3 text-decoration-none">
                    <i class="bi bi-shield-check display-6 mb-2"></i>
                    <span>Manage 2FA</span>
                  </router-link>
                </div>
                <div v-if="authStore.isAdmin" class="col-md-4 mb-3">
                  <router-link to="/users" class="btn btn-outline-success w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i class="bi bi-people display-6 mb-2"></i>
                    <span>Manage Users</span>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-clock-history me-2"></i>
                Recent Activity
              </h5>
            </div>
            <div class="card-body">
              <div class="list-group list-group-flush">
                <div class="list-group-item d-flex align-items-center">
                  <div class="me-3">
                    <i class="bi bi-box-arrow-in-right text-success"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-semibold">Logged in successfully</div>
                    <small class="text-muted">{{ formatDate(new Date()) }}</small>
                  </div>
                </div>
                <div class="list-group-item d-flex align-items-center">
                  <div class="me-3">
                    <i class="bi bi-person-check text-info"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-semibold">Profile accessed</div>
                    <small class="text-muted">{{ formatDate(authStore.user?.date_joined) }}</small>
                  </div>
                </div>
                <div class="list-group-item d-flex align-items-center">
                  <div class="me-3">
                    <i class="bi bi-person-plus text-primary"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-semibold">Account created</div>
                    <small class="text-muted">{{ formatDate(authStore.user?.date_joined) }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useToast } from 'vue-toastification'
import AppLayout from '@/components/AppLayout.vue'

const authStore = useAuthStore()
const toast = useToast()

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      // Silently handle error - user will see empty data
    }
  }
})
</script>

<style scoped>
.dashboard {
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

.btn {
  transition: all 0.2s ease-in-out;
}

.btn:hover {
  transform: translateY(-1px);
}

.list-group-item {
  border: none;
  padding: 1rem 0;
}

.list-group-item:not(:last-child) {
  border-bottom: 1px solid #dee2e6;
}
</style>
