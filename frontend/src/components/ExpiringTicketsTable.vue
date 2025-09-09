<template>
  <div class="expiring-tickets-table">
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white">
        <div class="d-flex justify-content-between align-items-center">
          <h6 class="card-title mb-0">
            <i class="bi bi-exclamation-triangle me-2 text-warning"></i>
            Expiring Tickets
            <span class="badge bg-warning text-dark ms-2" v-if="displayTickets.length">
              {{ displayTickets.length }}{{ showAll ? '' : `/${ticketsStore.expiringTickets.length}` }}
            </span>
          </h6>
          <div class="d-flex gap-2">
            <router-link to="/tickets" class="btn btn-sm btn-outline-primary">
              <i class="bi bi-ticket-perforated me-1"></i>
              Manage Tickets
            </router-link>
            <div v-if="!showAll && ticketsStore.expiringTickets.length > maxDisplay">
              <router-link to="/expiring-tickets" class="btn btn-sm btn-outline-warning">
                <i class="bi bi-eye me-1"></i>
                Show More
              </router-link>
            </div>
          </div>
        </div>
      </div>
      <div class="card-body p-0">
        <div v-if="ticketsStore.expiringTicketsLoading" class="text-center py-4">
          <div class="spinner-border spinner-border-sm text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 mb-0 text-muted small">Loading expiring tickets...</p>
        </div>
        
        <div v-else-if="ticketsStore.expiringTickets.length === 0" class="text-center py-4">
          <i class="bi bi-check-circle text-success fs-1"></i>
          <p class="mt-2 mb-0 text-muted">No tickets expiring soon</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th class="border-0">Ticket</th>
                <th class="border-0">Organization</th>
                <th class="border-0">Assigned To</th>
                <th class="border-0">Expires In</th>
                <th class="border-0">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ticket in displayTickets" :key="ticket.id">
                <td>
                  <div class="fw-semibold">{{ ticket.ticket_number }}</div>
                  <span class="badge" :class="getStatusBadgeClass(ticket.status)">
                    {{ ticket.status_display || ticket.status }}
                  </span>
                </td>
                <td>
                  <div>{{ ticket.organization }}</div>
                  <small class="text-muted">{{ ticket.location }}</small>
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar-xs bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2">
                      {{ getInitials(ticket.assigned_contractor.first_name, ticket.assigned_contractor.last_name) }}
                    </div>
                    <div>
                      <div class="fw-semibold small">
                        {{ ticket.assigned_contractor.first_name }} {{ ticket.assigned_contractor.last_name }}
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="text-warning fw-semibold">
                    <i class="bi bi-clock me-1"></i>
                    {{ getTimeRemaining(ticket.expiration_date) }}
                  </div>
                  <small class="text-muted">{{ formatDateTime(ticket.expiration_date) }}</small>
                </td>
                <td>
                  <button 
                    v-if="canRenew(ticket)"
                    class="btn btn-outline-success btn-sm"
                    @click="renewTicket(ticket)"
                    title="Renew (+15 days)"
                  >
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Renew
                  </button>
                  <span v-else class="text-muted small">No actions available</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useTicketsStore } from '@/stores/tickets.js'

// Props
const props = defineProps({
  showAll: {
    type: Boolean,
    default: false
  },
  maxDisplay: {
    type: Number,
    default: 3
  }
})

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()

// Computed
const displayTickets = computed(() => {
  if (props.showAll) {
    return ticketsStore.expiringTickets
  }
  return ticketsStore.expiringTickets.slice(0, props.maxDisplay)
})

// Methods
const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getInitials = (firstName, lastName) => {
  const first = firstName ? firstName.charAt(0).toUpperCase() : ''
  const last = lastName ? lastName.charAt(0).toUpperCase() : ''
  return first + last
}

const getStatusBadgeClass = (status) => {
  const statusClasses = {
    'open': 'bg-success',
    'in_progress': 'bg-warning text-dark',
    'pending': 'bg-info',
    'closed': 'bg-secondary',
    'expired': 'bg-danger'
  }
  return statusClasses[status] || 'bg-secondary'
}

const getTimeRemaining = (expirationDate) => {
  if (!expirationDate) return 'N/A'
  
  const now = new Date()
  const expiration = new Date(expirationDate)
  const diff = expiration - now
  
  if (diff <= 0) return 'Expired'
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  
  if (days > 0) {
    return `${days}d ${hours}h`
  } else {
    return `${hours}h`
  }
}

const canRenew = (ticket) => {
  if (!ticket || ticket.status === 'closed') return false
  if (authStore.isAdmin) return true
  if (authStore.isContractor && ticket.assigned_contractor?.id === authStore.user?.id) {
    return true
  }
  return false
}

const renewTicket = async (ticket) => {
  try {
    await ticketsStore.renewTicket(ticket)
    // Refresh expiring tickets after renewal
    await ticketsStore.loadExpiringTickets()
  } catch (error) {
    // Error handling is done in the store
  }
}
</script>

<style scoped>
.avatar-xs {
  width: 24px;
  height: 24px;
  font-size: 0.75rem;
}

.table th {
  font-weight: 600;
  color: #495057;
  font-size: 0.875rem;
}

.table td {
  vertical-align: middle;
  font-size: 0.875rem;
}

.table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.badge {
  font-size: 0.7em;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}
</style>
