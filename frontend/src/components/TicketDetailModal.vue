<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-ticket-perforated me-2"></i>
            {{ ticket.ticket_number }} - {{ ticket.organization }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        
        <div class="modal-body">
          <div class="row">
            <!-- Main Ticket Info -->
            <div class="col-lg-8">
              <div class="card border-0 shadow-sm mb-4">
                <div class="card-header bg-white">
                  <h6 class="card-title mb-0">
                    <i class="bi bi-info-circle me-2"></i>
                    Ticket Details
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row g-3">
                    <div class="col-md-6">
                      <label class="form-label text-muted">Organization</label>
                      <p class="fw-semibold">{{ ticket.organization }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Location</label>
                      <p class="fw-semibold">{{ ticket.location }}</p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Status</label>
                      <p>
                        <span class="badge" :class="statusBadgeClass">
                          {{ ticket.status_display }}
                        </span>
                      </p>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label text-muted">Expiration Status</label>
                      <p :class="expirationClass">
                        <i :class="expirationIcon" class="me-1"></i>
                        {{ expirationStatus }}
                      </p>
                    </div>
                    <div class="col-12" v-if="ticket.notes">
                      <label class="form-label text-muted">Notes</label>
                      <div class="notes-content">
                        {{ ticket.notes }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- User Information -->
              <div class="card border-0 shadow-sm mb-4">
                <div class="card-header bg-white">
                  <h6 class="card-title mb-0">
                    <i class="bi bi-people me-2"></i>
                    User Information
                  </h6>
                </div>
                <div class="card-body">
                  <div class="row g-3">
                    <div class="col-md-4">
                      <label class="form-label text-muted">Assigned Contractor</label>
                      <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2">
                          {{ getInitials(ticket.assigned_contractor.first_name, ticket.assigned_contractor.last_name) }}
                        </div>
                        <div>
                          <p class="mb-0 fw-semibold">
                            {{ ticket.assigned_contractor.first_name }} {{ ticket.assigned_contractor.last_name }}
                          </p>
                          <small class="text-muted">{{ ticket.assigned_contractor.email }}</small>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <label class="form-label text-muted">Created By</label>
                      <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center me-2">
                          {{ getInitials(ticket.created_by.first_name, ticket.created_by.last_name) }}
                        </div>
                        <div>
                          <p class="mb-0 fw-semibold">
                            {{ ticket.created_by.first_name }} {{ ticket.created_by.last_name }}
                          </p>
                          <small class="text-muted">{{ ticket.created_by.email }}</small>
                        </div>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <label class="form-label text-muted">Last Updated By</label>
                      <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-info text-white rounded-circle d-flex align-items-center justify-content-center me-2">
                          {{ getInitials(ticket.updated_by.first_name, ticket.updated_by.last_name) }}
                        </div>
                        <div>
                          <p class="mb-0 fw-semibold">
                            {{ ticket.updated_by.first_name }} {{ ticket.updated_by.last_name }}
                          </p>
                          <small class="text-muted">{{ ticket.updated_by.email }}</small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Activity Log -->
              <div class="card border-0 shadow-sm">
                <div class="card-header bg-white">
                  <h6 class="card-title mb-0">
                    <i class="bi bi-clock-history me-2"></i>
                    Activity Log
                  </h6>
                </div>
                <div class="card-body">
                  <div v-if="ticket.ticket_logs && ticket.ticket_logs.length > 0" class="timeline">
                    <div 
                      v-for="log in ticket.ticket_logs" 
                      :key="log.id"
                      class="timeline-item"
                    >
                      <div class="timeline-marker" :class="getLogMarkerClass(log.action)"></div>
                      <div class="timeline-content">
                        <div class="d-flex justify-content-between align-items-start">
                          <div>
                            <h6 class="mb-1">{{ log.action_display }}</h6>
                            <p class="text-muted mb-1">
                              by {{ log.action_by ? `${log.action_by.first_name} ${log.action_by.last_name}` : 'System' }}
                            </p>
                            <div v-if="log.details && Object.keys(log.details).length > 0" class="log-details">
                              <small class="text-muted">
                                <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
                              </small>
                            </div>
                          </div>
                          <small class="text-muted">
                            {{ formatDateTime(log.timestamp) }}
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-3">
                    <i class="bi bi-clock-history display-4 text-muted"></i>
                    <p class="text-muted mt-2">No activity logs available</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Sidebar -->
            <div class="col-lg-4">
              <!-- Quick Actions -->
              <div class="card border-0 shadow-sm mb-4">
                <div class="card-header bg-white">
                  <h6 class="card-title mb-0">
                    <i class="bi bi-lightning me-2"></i>
                    Quick Actions
                  </h6>
                </div>
                <div class="card-body">
                  <div class="d-grid gap-2">
                    <button 
                      v-if="canEdit"
                      class="btn btn-outline-primary"
                      @click="$emit('edit', ticket)"
                    >
                      <i class="bi bi-pencil me-2"></i>
                      Edit Ticket
                    </button>
                    
                    <button 
                      v-if="canRenew"
                      class="btn btn-outline-success"
                      @click="$emit('renew', ticket)"
                    >
                      <i class="bi bi-arrow-clockwise me-2"></i>
                      Renew (+15 days)
                    </button>
                    
                    <button 
                      v-if="authStore.isAdmin"
                      class="btn btn-outline-info"
                      @click="$emit('assign', ticket)"
                    >
                      <i class="bi bi-person-plus me-2"></i>
                      Reassign Contractor
                    </button>
                    
                    <button 
                      v-if="canClose"
                      class="btn btn-outline-danger"
                      @click="$emit('close-ticket', ticket)"
                    >
                      <i class="bi bi-x-circle me-2"></i>
                      Close Ticket
                    </button>
                  </div>
                </div>
              </div>

              <!-- Dates -->
              <div class="card border-0 shadow-sm mb-4">
                <div class="card-header bg-white">
                  <h6 class="card-title mb-0">
                    <i class="bi bi-calendar me-2"></i>
                    Important Dates
                  </h6>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label text-muted">Created Date</label>
                    <p class="mb-0">{{ formatDateTime(ticket.created_date) }}</p>
                  </div>
                  <div class="mb-3">
                    <label class="form-label text-muted">Expiration Date</label>
                    <p class="mb-0" :class="expirationClass">
                      {{ formatDateTime(ticket.expiration_date) }}
                    </p>
                  </div>
                  <div>
                    <label class="form-label text-muted">Last Updated</label>
                    <p class="mb-0">{{ formatDateTime(ticket.updated_at) }}</p>
                  </div>
                </div>
              </div>

              <!-- Expiration Countdown -->
              <div v-if="!ticket.is_expired" class="card border-0 shadow-sm">
                <div class="card-header bg-white">
                  <h6 class="card-title mb-0">
                    <i class="bi bi-stopwatch me-2"></i>
                    Time Remaining
                  </h6>
                </div>
                <div class="card-body text-center">
                  <div class="countdown" :class="expirationClass">
                    <h4 class="mb-1">{{ timeRemaining }}</h4>
                    <small class="text-muted">until expiration</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const authStore = useAuthStore()

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  ticket: {
    type: Object,
    required: true
  }
})

// Emits
defineEmits(['close', 'edit', 'renew', 'close-ticket', 'assign'])

// Computed properties
const statusBadgeClass = computed(() => {
  const classes = {
    'open': 'bg-success',
    'in_progress': 'bg-warning text-dark',
    'closed': 'bg-secondary'
  }
  return classes[props.ticket.status] || 'bg-secondary'
})

const expirationClass = computed(() => {
  if (props.ticket.is_expired) return 'text-danger'
  if (props.ticket.is_expiring_soon) return 'text-warning'
  return 'text-success'
})

const expirationIcon = computed(() => {
  if (props.ticket.is_expired) return 'bi bi-x-circle-fill'
  if (props.ticket.is_expiring_soon) return 'bi bi-exclamation-triangle-fill'
  return 'bi bi-check-circle-fill'
})

const expirationStatus = computed(() => {
  if (props.ticket.is_expired) return 'Expired'
  if (props.ticket.is_expiring_soon) return 'Expiring Soon'
  return 'Active'
})

const timeRemaining = computed(() => {
  if (props.ticket.is_expired) return 'Expired'
  
  const now = new Date()
  const expiration = new Date(props.ticket.expiration_date)
  const diff = expiration - now
  
  if (diff <= 0) return 'Expired'
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  
  if (days > 0) {
    return `${days} day${days !== 1 ? 's' : ''}, ${hours} hour${hours !== 1 ? 's' : ''}`
  } else {
    return `${hours} hour${hours !== 1 ? 's' : ''}`
  }
})

const canEdit = computed(() => {
  if (authStore.isAdmin) return true
  if (authStore.isContractor && props.ticket.assigned_contractor.id === authStore.user?.id) {
    return props.ticket.status !== 'closed'
  }
  return false
})

const canRenew = computed(() => {
  if (authStore.isAdmin) return true
  if (authStore.isContractor && props.ticket.assigned_contractor.id === authStore.user?.id) {
    return props.ticket.status !== 'closed'
  }
  return false
})

const canClose = computed(() => {
  if (props.ticket.status === 'closed') return false
  if (authStore.isAdmin) return true
  if (authStore.isContractor && props.ticket.assigned_contractor.id === authStore.user?.id) {
    return true
  }
  return false
})

// Methods
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

const getLogMarkerClass = (action) => {
  const classes = {
    'created': 'bg-success',
    'updated': 'bg-info',
    'status_changed': 'bg-warning',
    'assigned': 'bg-primary',
    'renewed': 'bg-success',
    'closed': 'bg-danger'
  }
  return classes[action] || 'bg-secondary'
}
</script>

<style scoped>
.modal {
  animation: fadeIn 0.15s ease-out;
}

.modal-dialog {
  animation: slideIn 0.15s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { 
    opacity: 0;
    transform: translateY(-50px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.avatar-sm {
  width: 32px;
  height: 32px;
  font-size: 0.875rem;
}

.notes-content {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.375rem;
  border-left: 4px solid #dee2e6;
  white-space: pre-wrap;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0.75rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #dee2e6;
}

.timeline-item {
  position: relative;
  margin-bottom: 1.5rem;
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0.25rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #dee2e6;
}

.timeline-content {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.375rem;
  border-left: 3px solid #dee2e6;
}

.log-details pre {
  background-color: #e9ecef;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  margin-top: 0.5rem;
  margin-bottom: 0;
}

.countdown {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
