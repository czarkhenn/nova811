<template>
  <AppLayout>
    <div class="tickets">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">
                <i class="bi bi-ticket-perforated me-2"></i>
                Tickets
              </h1>
              <p class="text-muted mb-0">
                {{ authStore.isAdmin ? 'Manage all tickets' : 'View your assigned tickets' }}
              </p>
            </div>
            <div v-if="authStore.isAdmin">
              <button 
                class="btn btn-primary"
                @click="ticketsStore.openCreateModal()"
              >
                <i class="bi bi-plus-lg me-1"></i>
                Create Ticket
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4" v-if="ticketsStore.stats">
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-primary mb-2">
                <i class="bi bi-list-task display-6"></i>
              </div>
              <h6 class="card-title">Total</h6>
              <h4 class="mb-0">{{ ticketsStore.stats.total }}</h4>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-success mb-2">
                <i class="bi bi-circle display-6"></i>
              </div>
              <h6 class="card-title">Open</h6>
              <h4 class="mb-0">{{ ticketsStore.stats.open }}</h4>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-warning mb-2">
                <i class="bi bi-arrow-clockwise display-6"></i>
              </div>
              <h6 class="card-title">In Progress</h6>
              <h4 class="mb-0">{{ ticketsStore.stats.in_progress }}</h4>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-secondary mb-2">
                <i class="bi bi-check-circle display-6"></i>
              </div>
              <h6 class="card-title">Closed</h6>
              <h4 class="mb-0">{{ ticketsStore.stats.closed }}</h4>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-danger mb-2">
                <i class="bi bi-exclamation-triangle display-6"></i>
              </div>
              <h6 class="card-title">Expiring</h6>
              <h4 class="mb-0">{{ ticketsStore.stats.expiring_soon }}</h4>
            </div>
          </div>
        </div>
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-dark mb-2">
                <i class="bi bi-x-circle display-6"></i>
              </div>
              <h6 class="card-title">Expired</h6>
              <h4 class="mb-0">{{ ticketsStore.stats.expired }}</h4>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-3">
                  <label class="form-label">Status</label>
                  <select 
                    class="form-select"
                    v-model="ticketsStore.filters.status"
                    @change="handleFilterChange"
                  >
                    <option value="">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <label class="form-label">Search</label>
                  <input 
                    type="text"
                    class="form-control"
                    placeholder="Search tickets..."
                    v-model="ticketsStore.filters.search"
                    @input="debounceSearch"
                  >
                </div>
                <div class="col-md-3">
                  <label class="form-label">Quick Filters</label>
                  <div class="btn-group w-100" role="group">
                    <input 
                      type="checkbox" 
                      class="btn-check" 
                      id="expiring-filter"
                      v-model="ticketsStore.filters.expiring_soon"
                      @change="handleFilterChange"
                    >
                    <label class="btn btn-outline-warning" for="expiring-filter">
                      <i class="bi bi-clock me-1"></i>
                      Expiring
                    </label>
                    <input 
                      type="checkbox" 
                      class="btn-check" 
                      id="expired-filter"
                      v-model="ticketsStore.filters.expired"
                      @change="handleFilterChange"
                    >
                    <label class="btn btn-outline-danger" for="expired-filter">
                      <i class="bi bi-x-circle me-1"></i>
                      Expired
                    </label>
                  </div>
                </div>
                <div class="col-md-3 d-flex align-items-end">
                  <button 
                    class="btn btn-outline-secondary w-100"
                    @click="clearFilters"
                  >
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Clear Filters
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tickets List -->
      <div class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-list me-2"></i>
                Tickets
                <span class="badge bg-secondary ms-2" v-if="ticketsStore.tickets.length">
                  {{ ticketsStore.tickets.length }}
                </span>
              </h5>
            </div>
            <div class="card-body p-0">
              <div v-if="ticketsStore.loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading tickets...</p>
              </div>
              
              <div v-else-if="ticketsStore.tickets.length === 0" class="text-center py-5">
                <i class="bi bi-inbox display-1 text-muted"></i>
                <h5 class="mt-3">No tickets found</h5>
                <p class="text-muted">
                  {{ ticketsStore.hasFilters ? 'Try adjusting your filters' : 'No tickets have been created yet' }}
                </p>
              </div>

              <div v-else>
                <TicketCard
                  v-for="ticket in ticketsStore.tickets"
                  :key="ticket.id"
                  :ticket="ticket"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Ticket Modal -->
      <TicketModal
        v-if="ticketsStore.showCreateModal || ticketsStore.showEditModal"
        :show="ticketsStore.showCreateModal || ticketsStore.showEditModal"
        :ticket="ticketsStore.selectedTicket"
        :contractors="ticketsStore.contractors"
        @close="ticketsStore.closeModal"
        @save="handleTicketSave"
      />

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
import TicketCard from '@/components/TicketCard.vue'
import TicketModal from '@/components/TicketModal.vue'
import TicketDetailModal from '@/components/TicketDetailModal.vue'
import AssignTicketModal from '@/components/AssignTicketModal.vue'

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()

// Search debounce
let searchTimeout = null

// Methods
const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    ticketsStore.loadTickets()
  }, 500)
}

const handleFilterChange = () => {
  ticketsStore.loadTickets()
}

const clearFilters = () => {
  ticketsStore.clearFilters()
  ticketsStore.loadTickets()
}

const handleTicketSave = async (ticketData) => {
  try {
    if (ticketsStore.selectedTicket) {
      await ticketsStore.updateTicket(ticketData)
    } else {
      await ticketsStore.createTicket(ticketData)
    }
  } catch (error) {
    // Error handling is done in the store
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    ticketsStore.loadTickets(),
    ticketsStore.loadStats(),
    ticketsStore.loadContractors(authStore.user?.role)
  ])
})
</script>

<style scoped>
.tickets {
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

.btn-check:checked + .btn {
  transform: none;
}
</style>
