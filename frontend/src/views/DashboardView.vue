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

      <!-- Expiring Tickets -->
      <div class="row mb-4">
        <div class="col-12">
          <ExpiringTicketsTable :max-display="5" />
        </div>
      </div>

      <!-- Ticket Statistics -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-success mb-2">
                <i class="bi bi-ticket-perforated display-4"></i>
              </div>
              <h5 class="card-title">Active Tickets</h5>
              <p class="card-text">
                <span class="h4 text-success">{{ ticketStats.active || 0 }}</span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-warning mb-2">
                <i class="bi bi-clock-history display-4"></i>
              </div>
              <h5 class="card-title">Expiring Soon</h5>
              <p class="card-text">
                <span class="h4 text-warning">{{ ticketStats.expiring_soon || 0 }}</span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-danger mb-2">
                <i class="bi bi-exclamation-triangle display-4"></i>
              </div>
              <h5 class="card-title">Expired</h5>
              <p class="card-text">
                <span class="h4 text-danger">{{ ticketStats.expired || 0 }}</span>
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-info mb-2">
                <i class="bi bi-check-circle display-4"></i>
              </div>
              <h5 class="card-title">Completed</h5>
              <p class="card-text">
                <span class="h4 text-info">{{ ticketStats.closed || 0 }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- User Profile Stats -->
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
                <div class="col-md-4 mb-3">
                  <router-link to="/tickets" class="btn btn-outline-warning w-100 h-100 d-flex flex-column align-items-center justify-content-center py-3">
                    <i class="bi bi-ticket-perforated display-6 mb-2"></i>
                    <span>Manage Tickets</span>
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
              <div v-if="recentLogs.length > 0" class="list-group list-group-flush">
                <div 
                  v-for="log in recentLogs" 
                  :key="log.id" 
                  class="list-group-item d-flex align-items-center"
                >
                  <div class="me-3">
                    <i :class="getLogIcon(log.action)" :style="{ color: getLogColor(log.action) }"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-semibold">{{ log.action_display }}</div>
                    <div v-if="log.ticket" class="small text-muted">
                      Ticket: {{ log.ticket.ticket_number }} - {{ log.ticket.organization }}
                    </div>
                    <div class="small text-muted">
                      by {{ log.user?.first_name }} {{ log.user?.last_name }}
                    </div>
                    <small class="text-muted">{{ formatDate(log.timestamp) }}</small>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <i class="bi bi-clock-history display-4 text-muted mb-3"></i>
                <p class="text-muted">No recent activity to display</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ticket Detail Modal -->
    <TicketDetailModal
      v-if="ticketsStore.showDetailModal"
      :show="ticketsStore.showDetailModal"
      :ticket="ticketsStore.selectedTicket"
      @close="ticketsStore.closeDetailModal"
      @renew="handleTicketRenew"
      @close-ticket="ticketsStore.closeTicket"
      @assign="(ticket) => ticketsStore.openAssignModal(ticket, authStore.user?.role)"
      @ticket-updated="handleTicketUpdated"
    />

    <!-- Assign Ticket Modal -->
    <AssignTicketModal
      v-if="ticketsStore.showAssignModal"
      :show="ticketsStore.showAssignModal"
      :ticket="ticketsStore.selectedTicket"
      :contractors="ticketsStore.contractors"
    />
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useTicketsStore } from '@/stores/tickets.js'
import { useToast } from 'vue-toastification'
import AppLayout from '@/components/AppLayout.vue'
import ExpiringTicketsTable from '@/components/ExpiringTicketsTable.vue'
import TicketDetailModal from '@/components/TicketDetailModal.vue'
import AssignTicketModal from '@/components/AssignTicketModal.vue'
import api from '@/services/api.js'

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()
const toast = useToast()

// Reactive data
const ticketStats = ref({
  active: 0,
  expiring_soon: 0,
  expired: 0,
  closed: 0
})
const recentLogs = ref([])
const loading = ref(false)

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

const getLogIcon = (action) => {
  const iconMap = {
    'created': 'bi bi-plus-circle',
    'updated': 'bi bi-pencil-square',
    'assigned': 'bi bi-person-plus',
    'renewed': 'bi bi-arrow-clockwise',
    'closed': 'bi bi-check-circle',
    'expired': 'bi bi-exclamation-triangle',
    'login': 'bi bi-box-arrow-in-right',
    'logout': 'bi bi-box-arrow-right',
    'profile_updated': 'bi bi-person-gear',
    'password_changed': 'bi bi-shield-lock',
    '2fa_enabled': 'bi bi-shield-check',
    '2fa_disabled': 'bi bi-shield-x'
  }
  return iconMap[action] || 'bi bi-circle'
}

const getLogColor = (action) => {
  const colorMap = {
    'created': '#198754',
    'updated': '#0d6efd',
    'assigned': '#6f42c1',
    'renewed': '#fd7e14',
    'closed': '#20c997',
    'expired': '#dc3545',
    'login': '#198754',
    'logout': '#6c757d',
    'profile_updated': '#0d6efd',
    'password_changed': '#fd7e14',
    '2fa_enabled': '#198754',
    '2fa_disabled': '#ffc107'
  }
  return colorMap[action] || '#6c757d'
}

const loadTicketStats = async () => {
  try {
    const response = await api.get('/tickets/stats/')
    const stats = response.data
    // Calculate active tickets as open + in_progress
    ticketStats.value = {
      ...stats,
      active: (stats.open || 0) + (stats.in_progress || 0)
    }
  } catch (error) {
    console.error('Error loading ticket stats:', error)
  }
}

const loadRecentLogs = async () => {
  try {
    const response = await api.get('/tickets/logs/users/', {
      params: { limit: 10 }
    })
    recentLogs.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading recent logs:', error)
  }
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadTicketStats(),
      loadRecentLogs()
    ])
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const handleTicketRenew = async (ticket, days = 15) => {
  try {
    await ticketsStore.renewTicket(ticket, days)
    // Refresh dashboard data after renewal
    await Promise.all([
      loadTicketStats(),
      ticketsStore.loadExpiringTickets()
    ])
  } catch (error) {
    // Error handling is done in the store
  }
}

const handleTicketUpdated = async (updatedTicket) => {
  // Refresh dashboard data after ticket update
  await Promise.all([
    loadTicketStats(),
    loadRecentLogs(),
    ticketsStore.loadExpiringTickets()
  ])
}

onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      // Silently handle error - user will see empty data
    }
  }
  
  // Load dashboard data
  await loadDashboardData()
  
  // Load expiring tickets for the table
  await ticketsStore.loadExpiringTickets()
  
  // Load contractors for ticket operations (only for admin users)
  await ticketsStore.loadContractors(authStore.user?.role)
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
