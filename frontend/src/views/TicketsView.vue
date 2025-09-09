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
                @click="showCreateModal = true"
              >
                <i class="bi bi-plus-lg me-1"></i>
                Create Ticket
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4" v-if="stats">
        <div class="col-md-2 mb-3">
          <div class="card border-0 shadow-sm">
            <div class="card-body text-center">
              <div class="text-primary mb-2">
                <i class="bi bi-list-task display-6"></i>
              </div>
              <h6 class="card-title">Total</h6>
              <h4 class="mb-0">{{ stats.total }}</h4>
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
              <h4 class="mb-0">{{ stats.open }}</h4>
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
              <h4 class="mb-0">{{ stats.in_progress }}</h4>
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
              <h4 class="mb-0">{{ stats.closed }}</h4>
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
              <h4 class="mb-0">{{ stats.expiring_soon }}</h4>
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
              <h4 class="mb-0">{{ stats.expired }}</h4>
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
                    v-model="filters.status"
                    @change="loadTickets"
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
                    v-model="filters.search"
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
                      v-model="filters.expiring_soon"
                      @change="loadTickets"
                    >
                    <label class="btn btn-outline-warning" for="expiring-filter">
                      <i class="bi bi-clock me-1"></i>
                      Expiring
                    </label>
                    <input 
                      type="checkbox" 
                      class="btn-check" 
                      id="expired-filter"
                      v-model="filters.expired"
                      @change="loadTickets"
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
                <span class="badge bg-secondary ms-2" v-if="tickets.length">
                  {{ tickets.length }}
                </span>
              </h5>
            </div>
            <div class="card-body p-0">
              <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading tickets...</p>
              </div>
              
              <div v-else-if="tickets.length === 0" class="text-center py-5">
                <i class="bi bi-inbox display-1 text-muted"></i>
                <h5 class="mt-3">No tickets found</h5>
                <p class="text-muted">
                  {{ hasFilters ? 'Try adjusting your filters' : 'No tickets have been created yet' }}
                </p>
              </div>

              <div v-else>
                <TicketCard
                  v-for="ticket in tickets"
                  :key="ticket.id"
                  :ticket="ticket"
                  @view="viewTicket"
                  @edit="editTicket"
                  @renew="renewTicket"
                  @close="closeTicket"
                  @assign="assignTicket"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Ticket Modal -->
      <TicketModal
        v-if="showCreateModal || showEditModal"
        :show="showCreateModal || showEditModal"
        :ticket="selectedTicket"
        :contractors="contractors"
        @close="closeModal"
        @save="handleTicketSave"
      />

      <!-- Ticket Detail Modal -->
      <TicketDetailModal
        v-if="showDetailModal"
        :show="showDetailModal"
        :ticket="selectedTicket"
        @close="showDetailModal = false"
        @edit="editTicket"
        @renew="renewTicket"
        @close-ticket="closeTicket"
        @assign="assignTicket"
      />

      <!-- Assign Ticket Modal -->
      <AssignTicketModal
        v-if="showAssignModal"
        :show="showAssignModal"
        :ticket="selectedTicket"
        :contractors="contractors"
        @close="showAssignModal = false"
        @assign="handleTicketAssign"
      />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useToast } from 'vue-toastification'
import AppLayout from '@/components/AppLayout.vue'
import TicketCard from '@/components/TicketCard.vue'
import TicketModal from '@/components/TicketModal.vue'
import TicketDetailModal from '@/components/TicketDetailModal.vue'
import AssignTicketModal from '@/components/AssignTicketModal.vue'
import api from '@/services/api.js'

const authStore = useAuthStore()
const toast = useToast()

// Reactive data
const loading = ref(false)
const tickets = ref([])
const stats = ref(null)
const contractors = ref([])

// Modal states
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDetailModal = ref(false)
const showAssignModal = ref(false)
const selectedTicket = ref(null)

// Filters
const filters = ref({
  status: '',
  search: '',
  expiring_soon: false,
  expired: false
})

// Search debounce
let searchTimeout = null

// Computed
const hasFilters = computed(() => {
  return filters.value.status || 
         filters.value.search || 
         filters.value.expiring_soon || 
         filters.value.expired
})

// Methods
const loadTickets = async () => {
  try {
    loading.value = true
    
    const params = new URLSearchParams()
    if (filters.value.status) params.append('status', filters.value.status)
    if (filters.value.search) params.append('search', filters.value.search)
    if (filters.value.expiring_soon) params.append('expiring_soon', 'true')
    if (filters.value.expired) params.append('expired', 'true')
    
    const response = await api.get(`/tickets/?${params.toString()}`)
    tickets.value = response.data.results || response.data
  } catch (error) {
    console.error('Error loading tickets:', error)
    toast.error('Failed to load tickets')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await api.get('/tickets/stats/')
    stats.value = response.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadContractors = async () => {
  if (!authStore.isAdmin) return
  
  try {
    const response = await api.get('/tickets/contractors/')
    contractors.value = response.data
  } catch (error) {
    console.error('Error loading contractors:', error)
  }
}

const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadTickets()
  }, 500)
}

const clearFilters = () => {
  filters.value = {
    status: '',
    search: '',
    expiring_soon: false,
    expired: false
  }
  loadTickets()
}

const viewTicket = (ticket) => {
  selectedTicket.value = ticket
  showDetailModal.value = true
}

const editTicket = (ticket) => {
  selectedTicket.value = ticket
  showEditModal.value = true
}

const renewTicket = async (ticket, days = 15) => {
  try {
    await api.post(`/tickets/${ticket.id}/renew/`, { days })
    toast.success(`Ticket renewed for ${days} days`)
    loadTickets()
    loadStats()
  } catch (error) {
    console.error('Error renewing ticket:', error)
    toast.error('Failed to renew ticket')
  }
}

const closeTicket = async (ticket, reason = '') => {
  try {
    await api.post(`/tickets/${ticket.id}/close/`, { reason })
    toast.success('Ticket closed successfully')
    loadTickets()
    loadStats()
  } catch (error) {
    console.error('Error closing ticket:', error)
    toast.error('Failed to close ticket')
  }
}

const assignTicket = (ticket) => {
  selectedTicket.value = ticket
  showAssignModal.value = true
}

const handleTicketAssign = async (ticketId, contractorId) => {
  try {
    await api.post(`/tickets/${ticketId}/assign/`, { 
      assigned_contractor_id: contractorId 
    })
    toast.success('Ticket assigned successfully')
    showAssignModal.value = false
    loadTickets()
  } catch (error) {
    console.error('Error assigning ticket:', error)
    toast.error('Failed to assign ticket')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedTicket.value = null
}

const handleTicketSave = async (ticketData) => {
  try {
    if (selectedTicket.value) {
      // Update existing ticket
      await api.put(`/tickets/${selectedTicket.value.id}/`, ticketData)
      toast.success('Ticket updated successfully')
    } else {
      // Create new ticket
      await api.post('/tickets/', ticketData)
      toast.success('Ticket created successfully')
    }
    
    closeModal()
    loadTickets()
    loadStats()
  } catch (error) {
    console.error('Error saving ticket:', error)
    toast.error('Failed to save ticket')
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadTickets(),
    loadStats(),
    loadContractors()
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
