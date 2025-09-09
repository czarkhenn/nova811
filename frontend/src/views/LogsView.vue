<template>
  <AppLayout>
    <div class="logs">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">
                <i class="bi bi-journal-text me-2"></i>
                Activity Logs
              </h1>
              <p class="text-muted mb-0">
                {{ authStore.isAdmin ? 'View system activity logs' : 'View your activity logs' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <ul class="nav nav-tabs card-header-tabs" role="tablist">
                <li class="nav-item" role="presentation">
                  <button 
                    class="nav-link"
                    :class="{ active: activeTab === 'user-logs' }"
                    @click="setActiveTab('user-logs')"
                    type="button"
                  >
                    <i class="bi bi-person-lines-fill me-2"></i>
                    User Logs
                    <span class="badge bg-secondary ms-2" v-if="userLogs.length">
                      {{ userLogs.length }}
                    </span>
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button 
                    class="nav-link"
                    :class="{ active: activeTab === 'ticket-logs' }"
                    @click="setActiveTab('ticket-logs')"
                    type="button"
                  >
                    <i class="bi bi-ticket-perforated me-2"></i>
                    Ticket Logs
                    <span class="badge bg-secondary ms-2" v-if="ticketLogs.length">
                      {{ ticketLogs.length }}
                    </span>
                  </button>
                </li>
              </ul>
            </div>
            <div class="card-body">
              <!-- Filters -->
              <div class="row mb-3">
                <div class="col-md-4">
                  <label class="form-label">Limit</label>
                  <select 
                    class="form-select"
                    v-model="filters.limit"
                    @change="loadLogs"
                  >
                    <option value="25">25 entries</option>
                    <option value="50">50 entries</option>
                    <option value="100">100 entries</option>
                    <option value="200">200 entries</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Search</label>
                  <input 
                    type="text"
                    class="form-control"
                    placeholder="Search logs..."
                    v-model="filters.search"
                    @input="debounceSearch"
                  >
                </div>
                <div class="col-md-4 d-flex align-items-end">
                  <button 
                    class="btn btn-outline-secondary"
                    @click="refreshLogs"
                    :disabled="loading"
                  >
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Refresh
                  </button>
                </div>
              </div>

              <!-- Tab Content -->
              <div class="tab-content">
                <!-- User Logs Tab -->
                <div 
                  class="tab-pane fade"
                  :class="{ 'show active': activeTab === 'user-logs' }"
                >
                  <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-muted">Loading user logs...</p>
                  </div>
                  
                  <div v-else-if="filteredUserLogs.length === 0" class="text-center py-5">
                    <i class="bi bi-journal display-1 text-muted"></i>
                    <h5 class="mt-3">No user logs found</h5>
                    <p class="text-muted">
                      {{ filters.search ? 'Try adjusting your search' : 'No user activity recorded yet' }}
                    </p>
                  </div>

                  <div v-else class="table-responsive">
                    <table class="table table-hover">
                      <thead class="table-light">
                        <tr>
                          <th>Timestamp</th>
                          <th>User</th>
                          <th>Action</th>
                          <th>Related Ticket</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="log in filteredUserLogs" :key="log.id">
                          <td>
                            <small class="text-muted">
                              {{ formatDateTime(log.timestamp) }}
                            </small>
                          </td>
                          <td>
                            <div class="d-flex align-items-center">
                              <div class="avatar-sm me-2">
                                <div class="avatar-title bg-primary rounded-circle">
                                  {{ getUserInitials(log.user) }}
                                </div>
                              </div>
                              <div>
                                <div class="fw-medium">{{ log.user.first_name }} {{ log.user.last_name }}</div>
                                <small class="text-muted">{{ log.user.email }}</small>
                              </div>
                            </div>
                          </td>
                          <td>
                            <span class="badge" :class="getActionBadgeClass(log.action)">
                              {{ log.action_display || log.action }}
                            </span>
                          </td>
                          <td>
                            <button 
                              v-if="log.related_ticket" 
                              class="badge bg-light text-dark border-0 text-decoration-none"
                              @click="viewTicket(log.related_ticket)"
                              style="cursor: pointer;"
                            >
                              {{ log.related_ticket.ticket_number }}
                            </button>
                            <span v-else class="text-muted">-</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Ticket Logs Tab -->
                <div 
                  class="tab-pane fade"
                  :class="{ 'show active': activeTab === 'ticket-logs' }"
                >
                  <div v-if="loading" class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-muted">Loading ticket logs...</p>
                  </div>
                  
                  <div v-else-if="filteredTicketLogs.length === 0" class="text-center py-5">
                    <i class="bi bi-ticket display-1 text-muted"></i>
                    <h5 class="mt-3">No ticket logs found</h5>
                    <p class="text-muted">
                      {{ filters.search ? 'Try adjusting your search' : 'No ticket activity recorded yet' }}
                    </p>
                  </div>

                  <div v-else class="table-responsive">
                    <table class="table table-hover">
                      <thead class="table-light">
                        <tr>
                          <th>Timestamp</th>
                          <th>Ticket</th>
                          <th>Action By</th>
                          <th>Action</th>
                          <th>Previous Values</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="log in filteredTicketLogs" :key="log.id">
                          <td>
                            <small class="text-muted">
                              {{ formatDateTime(log.timestamp) }}
                            </small>
                          </td>
                          <td>
                            <div v-if="log.ticket">
                              <button 
                                class="fw-medium bg-transparent border-0 text-primary text-decoration-underline p-0"
                                @click="viewTicket(log.ticket)"
                                style="cursor: pointer;"
                              >
                                {{ log.ticket.ticket_number }}
                              </button>
                              <br>
                              <small class="text-muted">{{ log.ticket.organization }}</small>
                            </div>
                            <span v-else class="text-muted">-</span>
                          </td>
                          <td>
                            <div v-if="log.action_by" class="d-flex align-items-center">
                              <div class="avatar-sm me-2">
                                <div class="avatar-title bg-secondary rounded-circle">
                                  {{ getUserInitials(log.action_by) }}
                                </div>
                              </div>
                              <div>
                                <div class="fw-medium">{{ log.action_by.first_name }} {{ log.action_by.last_name }}</div>
                                <small class="text-muted">{{ log.action_by.email }}</small>
                              </div>
                            </div>
                            <span v-else class="text-muted">System</span>
                          </td>
                          <td>
                            <span class="badge" :class="getActionBadgeClass(log.action)">
                              {{ log.action_display || log.action }}
                            </span>
                          </td>
                          <td>
                            <button 
                              v-if="log.previous_values"
                              class="btn btn-sm btn-outline-secondary"
                              @click="showPreviousValues(log)"
                            >
                              <i class="bi bi-eye me-1"></i>
                              View
                            </button>
                            <span v-else class="text-muted">-</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Previous Values Modal -->
      <div class="modal fade" id="previousValuesModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Previous Values</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div v-if="selectedLog">
                <h6>Ticket: {{ selectedLog.ticket.ticket_number }}</h6>
                <p class="text-muted mb-3">Action: {{ selectedLog.action }} by {{ selectedLog.action_by.first_name }} {{ selectedLog.action_by.last_name }}</p>
                
                <div class="table-responsive">
                  <table class="table table-sm">
                    <thead>
                      <tr>
                        <th>Field</th>
                        <th>Previous Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(value, field) in selectedLog.previous_values" :key="field">
                        <td class="fw-medium">{{ formatFieldName(field) }}</td>
                        <td>
                          <code class="text-muted">{{ value || 'null' }}</code>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>

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
        v-if="ticketsStore.showAssignModal"
        :show="ticketsStore.showAssignModal"
        :ticket="ticketsStore.selectedTicket"
        :contractors="ticketsStore.contractors"
      />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'
import { useTicketsStore } from '@/stores/tickets.js'
import { useToast } from 'vue-toastification'
import AppLayout from '@/components/AppLayout.vue'
import TicketDetailModal from '@/components/TicketDetailModal.vue'
import AssignTicketModal from '@/components/AssignTicketModal.vue'
import api from '@/services/api.js'

const authStore = useAuthStore()
const ticketsStore = useTicketsStore()
const toast = useToast()

// Reactive data
const loading = ref(false)
const activeTab = ref('user-logs')
const userLogs = ref([])
const ticketLogs = ref([])
const selectedLog = ref(null)
const selectedTicket = ref(null)
const contractors = ref([])

// Modal states
const showDetailModal = ref(false)
const showAssignModal = ref(false)

// Filters
const filters = ref({
  limit: 50,
  search: ''
})

// Search debounce
let searchTimeout = null

// Computed
const filteredUserLogs = computed(() => {
  if (!filters.value.search) return userLogs.value
  
  const search = filters.value.search.toLowerCase()
  return userLogs.value.filter(log => {
    try {
      return (
        (log.user?.first_name?.toLowerCase().includes(search)) ||
        (log.user?.last_name?.toLowerCase().includes(search)) ||
        (log.user?.email?.toLowerCase().includes(search)) ||
        (log.action?.toLowerCase().includes(search)) ||
        (log.action_display?.toLowerCase().includes(search)) ||
        (log.related_ticket?.ticket_number?.toLowerCase().includes(search))
      )
    } catch (e) {
      console.warn('Error filtering user log:', e, log)
      return false
    }
  })
})

const filteredTicketLogs = computed(() => {
  if (!filters.value.search) return ticketLogs.value
  
  const search = filters.value.search.toLowerCase()
  return ticketLogs.value.filter(log => {
    try {
      return (
        (log.ticket?.ticket_number?.toLowerCase().includes(search)) ||
        (log.ticket?.organization?.toLowerCase().includes(search)) ||
        (log.action_by?.first_name?.toLowerCase().includes(search)) ||
        (log.action_by?.last_name?.toLowerCase().includes(search)) ||
        (log.action_by?.email?.toLowerCase().includes(search)) ||
        (log.action?.toLowerCase().includes(search)) ||
        (log.action_display?.toLowerCase().includes(search))
      )
    } catch (e) {
      console.warn('Error filtering ticket log:', e, log)
      return false
    }
  })
})

// Methods
const setActiveTab = (tab) => {
  activeTab.value = tab
  if ((tab === 'user-logs' && userLogs.value.length === 0) ||
      (tab === 'ticket-logs' && ticketLogs.value.length === 0)) {
    loadLogs()
  }
}

const loadLogs = async () => {
  if (activeTab.value === 'user-logs') {
    await loadUserLogs()
  } else {
    await loadTicketLogs()
  }
}

const loadUserLogs = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    params.append('limit', filters.value.limit)
    
    const response = await api.get(`/tickets/logs/users/?${params.toString()}`)
    userLogs.value = response.data.results || []
  } catch (error) {
    console.error('Error loading user logs:', error)
    toast.error('Failed to load user logs')
  } finally {
    loading.value = false
  }
}

const loadTicketLogs = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    params.append('limit', filters.value.limit)
    
    const response = await api.get(`/tickets/logs/tickets/?${params.toString()}`)
    ticketLogs.value = response.data.results || []
  } catch (error) {
    console.error('Error loading ticket logs:', error)
    toast.error('Failed to load ticket logs')
  } finally {
    loading.value = false
  }
}

const refreshLogs = () => {
  loadLogs()
}

const debounceSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    // Search is handled by computed properties, no need to reload
  }, 300)
}

const showPreviousValues = (log) => {
  selectedLog.value = log
  const modal = new bootstrap.Modal(document.getElementById('previousValuesModal'))
  modal.show()
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getUserInitials = (user) => {
  if (!user) return '?'
  const first = user.first_name ? user.first_name.charAt(0) : ''
  const last = user.last_name ? user.last_name.charAt(0) : ''
  return (first + last).toUpperCase() || user.email.charAt(0).toUpperCase()
}

const getActionBadgeClass = (action) => {
  const actionLower = action.toLowerCase()
  if (actionLower.includes('create')) return 'bg-success'
  if (actionLower.includes('update') || actionLower.includes('edit')) return 'bg-warning'
  if (actionLower.includes('delete') || actionLower.includes('close')) return 'bg-danger'
  if (actionLower.includes('assign')) return 'bg-info'
  if (actionLower.includes('renew')) return 'bg-primary'
  if (actionLower.includes('login')) return 'bg-success'
  if (actionLower.includes('logout')) return 'bg-secondary'
  return 'bg-light text-dark'
}

const formatFieldName = (field) => {
  return field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
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

const viewTicket = async (ticket) => {
  try {
    // Fetch full ticket details
    const response = await api.get(`/tickets/${ticket.id}/`)
    selectedTicket.value = response.data
    showDetailModal.value = true
  } catch (error) {
    console.error('Error loading ticket details:', error)
    toast.error('Failed to load ticket details')
  }
}

const editTicket = (ticket) => {
  // For now, just show a message that editing is not available from logs
  toast.info('Please go to the Tickets page to edit tickets')
}

const renewTicket = async (ticket, days = 15) => {
  try {
    await api.post(`/tickets/${ticket.id}/renew/`, { days })
    toast.success(`Ticket renewed for ${days} days`)
    // Refresh the ticket details if modal is open
    if (showDetailModal.value && selectedTicket.value?.id === ticket.id) {
      await viewTicket(ticket)
    }
  } catch (error) {
    console.error('Error renewing ticket:', error)
    toast.error('Failed to renew ticket')
  }
}

const closeTicket = async (ticket, reason = '') => {
  try {
    await api.post(`/tickets/${ticket.id}/close/`, { reason })
    toast.success('Ticket closed successfully')
    showDetailModal.value = false
    // Refresh logs to show updated status
    loadLogs()
  } catch (error) {
    console.error('Error closing ticket:', error)
    toast.error('Failed to close ticket')
  }
}

const assignTicket = (ticket) => {
  ticketsStore.openAssignModal(ticket, authStore.user?.role)
}

const handleTicketAssign = async (ticketId, contractorId) => {
  try {
    await api.post(`/tickets/${ticketId}/assign/`, { 
      assigned_contractor_id: contractorId 
    })
    toast.success('Ticket assigned successfully')
    showAssignModal.value = false
    // Refresh the ticket details if modal is open
    if (showDetailModal.value && selectedTicket.value?.id === ticketId) {
      const response = await api.get(`/tickets/${ticketId}/`)
      selectedTicket.value = response.data
    }
    // Refresh logs to show the assignment
    loadLogs()
  } catch (error) {
    console.error('Error assigning ticket:', error)
    toast.error('Failed to assign ticket')
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    loadUserLogs(),
    loadContractors()
  ])
})
</script>

<style scoped>
.logs {
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

.avatar-sm {
  width: 32px;
  height: 32px;
}

.avatar-title {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
  background: none;
}

.nav-tabs .nav-link.active {
  color: #495057;
  background-color: #fff;
  border-color: #dee2e6 #dee2e6 #fff;
}

.table th {
  border-top: none;
  font-weight: 600;
  font-size: 0.875rem;
}

.table td {
  vertical-align: middle;
}

.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
