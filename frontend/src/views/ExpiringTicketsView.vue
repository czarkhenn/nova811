<template>
  <AppLayout>
    <div class="expiring-tickets">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">
                <i class="bi bi-clock-history me-2"></i>
                Expiring Tickets
              </h1>
              <p class="text-muted mb-0">
                Tickets expiring within 48 hours
              </p>
            </div>
            <div>
              <router-link to="/tickets" class="btn btn-outline-primary">
                <i class="bi bi-arrow-left me-1"></i>
                Back to Tickets
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Expiring Tickets Table -->
      <div class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-exclamation-triangle me-2 text-warning"></i>
                Expiring Tickets
                <span class="badge bg-warning text-dark ms-2" v-if="ticketsStore.expiringTickets.length">
                  {{ ticketsStore.expiringTickets.length }}
                </span>
              </h5>
            </div>
            <div class="card-body p-0">
              <div v-if="ticketsStore.expiringTicketsLoading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading expiring tickets...</p>
              </div>
              
              <div v-else-if="ticketsStore.expiringTickets.length === 0" class="text-center py-5">
                <i class="bi bi-check-circle display-1 text-success"></i>
                <h5 class="mt-3">No Expiring Tickets</h5>
                <p class="text-muted">
                  Great! No tickets are expiring within the next 48 hours.
                </p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover mb-0">
                  <thead class="table-light">
                    <tr>
                      <th>Ticket</th>
                      <th>Organization</th>
                      <th>Location</th>
                      <th>Assigned To</th>
                      <th>Status</th>
                      <th>Expires In</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ticket in ticketsStore.expiringTickets" :key="ticket.id">
                      <td>
                        <div class="fw-semibold">{{ ticket.ticket_number }}</div>
                        <small class="text-muted">{{ formatDate(ticket.created_date) }}</small>
                      </td>
                      <td>{{ ticket.organization }}</td>
                      <td>{{ ticket.location }}</td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2">
                            {{ getInitials(ticket.assigned_contractor.first_name, ticket.assigned_contractor.last_name) }}
                          </div>
                          <div>
                            <div class="fw-semibold">
                              {{ ticket.assigned_contractor.first_name }} {{ ticket.assigned_contractor.last_name }}
                            </div>
                            <small class="text-muted">{{ ticket.assigned_contractor.email }}</small>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span class="badge" :class="getStatusBadgeClass(ticket.status)">
                          {{ ticket.status_display || ticket.status }}
                        </span>
                      </td>
                      <td>
                        <div class="text-warning fw-semibold">
                          <i class="bi bi-clock me-1"></i>
                          {{ getTimeRemaining(ticket.expiration_date) }}
                        </div>
                        <small class="text-muted">{{ formatDateTime(ticket.expiration_date) }}</small>
                      </td>
                      <td>
                        <div class="btn-group btn-group-sm" role="group">
                          <button 
                            class="btn btn-outline-primary"
                            @click="ticketsStore.selectTicket(ticket)"
                            title="View Details"
                          >
                            <i class="bi bi-eye"></i>
                          </button>
                          <button 
                            v-if="canRenew(ticket)"
                            class="btn btn-outline-success"
                            @click="renewTicket(ticket)"
                            title="Renew (+15 days)"
                          >
                            <i class="bi bi-arrow-clockwise"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
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
        @edit="ticketsStore.openEditModal"
        @renew="ticketsStore.renewTicket"
        @close-ticket="ticketsStore.closeTicket"
        @assign="(ticket) => ticketsStore.openAssignModal(ticket, authStore.user?.role)"
      />

      <!-- Assign Ticket Modal -->
      <AssignTicketModal
        v-if="ticketsStore.showAssignModal"
        :show="ticketsStore.showAssignModal"
        :ticket="ticketsStore.selectedTicket"
        :contractors="ticketsStore.contractors"
      />
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useTicketsStore } from '@/stores/tickets.js'
import AppLayout from '@/components/AppLayout.vue'
import TicketDetailModal from '@/components/TicketDetailModal.vue'
import AssignTicketModal from '@/components/AssignTicketModal.vue'

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()

// Methods
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
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

// Lifecycle
onMounted(async () => {
  await Promise.all([
    ticketsStore.loadExpiringTickets(),
    ticketsStore.loadContractors(authStore.user?.role)
  ])
})
</script>

<style scoped>
.expiring-tickets {
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

.avatar-sm {
  width: 32px;
  height: 32px;
  font-size: 0.875rem;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.table td {
  vertical-align: middle;
}

.table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
