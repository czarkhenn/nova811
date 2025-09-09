<template>
  <div class="modal fade" :id="modalId" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-journal-text me-2"></i>
            Audit Trail
            <span v-if="ticket" class="text-muted">- {{ ticket.ticket_number }}</span>
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div v-if="ticket" class="mb-4">
            <div class="row">
              <div class="col-md-6">
                <h6>Ticket Information</h6>
                <p class="mb-1"><strong>Organization:</strong> {{ ticket.organization }}</p>
                <p class="mb-1"><strong>Location:</strong> {{ ticket.location }}</p>
                <p class="mb-1"><strong>Status:</strong> 
                  <span class="badge" :class="getStatusBadgeClass(ticket.status)">
                    {{ formatStatus(ticket.status) }}
                  </span>
                </p>
              </div>
              <div class="col-md-6">
                <p class="mb-1"><strong>Created:</strong> {{ formatDateTime(ticket.created_date) }}</p>
                <p class="mb-1"><strong>Expires:</strong> {{ formatDateTime(ticket.expiration_date) }}</p>
                <p class="mb-1"><strong>Assigned to:</strong> 
                  {{ ticket.assigned_contractor ? `${ticket.assigned_contractor.first_name} ${ticket.assigned_contractor.last_name}` : 'Unassigned' }}
                </p>
              </div>
            </div>
          </div>

          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading audit trail...</p>
          </div>

          <div v-else-if="auditTrail.length === 0" class="text-center py-5">
            <i class="bi bi-journal display-1 text-muted"></i>
            <h5 class="mt-3">No audit trail found</h5>
            <p class="text-muted">No activity has been recorded for this ticket yet.</p>
          </div>

          <div v-else>
            <h6 class="mb-3">
              Activity Timeline
              <span class="badge bg-secondary ms-2">{{ auditTrail.length }} entries</span>
            </h6>
            
            <div class="timeline">
              <div 
                v-for="(entry, index) in auditTrail" 
                :key="index"
                class="timeline-item"
                :class="{ 'timeline-item-last': index === auditTrail.length - 1 }"
              >
                <div class="timeline-marker" :class="getTimelineMarkerClass(entry.action)">
                  <i :class="getActionIcon(entry.action)"></i>
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 class="mb-1">
                          <span class="badge" :class="getActionBadgeClass(entry.action)">
                            {{ entry.action }}
                          </span>
                          <span class="ms-2 text-muted">{{ entry.type === 'ticket_action' ? 'Ticket Action' : 'User Action' }}</span>
                        </h6>
                        <div class="d-flex align-items-center text-muted">
                          <div class="avatar-xs me-2">
                            <div class="avatar-title bg-light text-dark rounded-circle">
                              {{ getUserInitials(entry.user) }}
                            </div>
                          </div>
                          <span>{{ entry.user.first_name }} {{ entry.user.last_name }}</span>
                          <span class="mx-2">•</span>
                          <small>{{ formatDateTime(entry.timestamp) }}</small>
                          <span v-if="entry.ip_address" class="mx-2">•</span>
                          <small v-if="entry.ip_address" class="font-monospace">{{ entry.ip_address }}</small>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="entry.details" class="timeline-body mt-2">
                    <p class="mb-0">{{ entry.details }}</p>
                  </div>

                  <div v-if="entry.previous_values && Object.keys(entry.previous_values).length > 0" class="timeline-changes mt-3">
                    <h6 class="text-muted mb-2">
                      <i class="bi bi-arrow-left-right me-1"></i>
                      Previous Values
                    </h6>
                    <div class="table-responsive">
                      <table class="table table-sm table-bordered">
                        <thead class="table-light">
                          <tr>
                            <th style="width: 30%;">Field</th>
                            <th>Previous Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(value, field) in entry.previous_values" :key="field">
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
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" @click="refreshAuditTrail" :disabled="loading">
            <i class="bi bi-arrow-clockwise me-1"></i>
            Refresh
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api.js'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  ticket: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const toast = useToast()

// Reactive data
const loading = ref(false)
const auditTrail = ref([])

// Computed
const modalId = computed(() => `auditTrailModal-${props.ticket?.id || 'default'}`)

// Methods
const loadAuditTrail = async () => {
  if (!props.ticket?.id) return
  
  try {
    loading.value = true
    const response = await api.get(`/tickets/${props.ticket.id}/audit/`)
    auditTrail.value = response.data.results || []
  } catch (error) {
    toast.error('Failed to load audit trail')
  } finally {
    loading.value = false
  }
}

const refreshAuditTrail = () => {
  loadAuditTrail()
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

const formatStatus = (status) => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatFieldName = (field) => {
  return field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getUserInitials = (user) => {
  if (!user) return '?'
  const first = user.first_name ? user.first_name.charAt(0) : ''
  const last = user.last_name ? user.last_name.charAt(0) : ''
  return (first + last).toUpperCase() || user.email.charAt(0).toUpperCase()
}

const getStatusBadgeClass = (status) => {
  switch (status) {
    case 'open': return 'bg-success'
    case 'in_progress': return 'bg-warning'
    case 'closed': return 'bg-secondary'
    default: return 'bg-light text-dark'
  }
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

const getTimelineMarkerClass = (action) => {
  const actionLower = action.toLowerCase()
  if (actionLower.includes('create')) return 'timeline-marker-success'
  if (actionLower.includes('update') || actionLower.includes('edit')) return 'timeline-marker-warning'
  if (actionLower.includes('delete') || actionLower.includes('close')) return 'timeline-marker-danger'
  if (actionLower.includes('assign')) return 'timeline-marker-info'
  if (actionLower.includes('renew')) return 'timeline-marker-primary'
  return 'timeline-marker-secondary'
}

const getActionIcon = (action) => {
  const actionLower = action.toLowerCase()
  if (actionLower.includes('create')) return 'bi bi-plus-circle'
  if (actionLower.includes('update') || actionLower.includes('edit')) return 'bi bi-pencil-square'
  if (actionLower.includes('delete')) return 'bi bi-trash'
  if (actionLower.includes('close')) return 'bi bi-x-circle'
  if (actionLower.includes('assign')) return 'bi bi-person-check'
  if (actionLower.includes('renew')) return 'bi bi-arrow-clockwise'
  if (actionLower.includes('login')) return 'bi bi-box-arrow-in-right'
  if (actionLower.includes('logout')) return 'bi bi-box-arrow-right'
  return 'bi bi-circle'
}

// Watchers
watch(() => props.show, (newValue) => {
  if (newValue && props.ticket) {
    loadAuditTrail()
  }
})

watch(() => props.ticket, (newTicket) => {
  if (newTicket && props.show) {
    loadAuditTrail()
  }
})
</script>

<style scoped>
.avatar-xs {
  width: 24px;
  height: 24px;
}

.avatar-title {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 600;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 1rem;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #dee2e6;
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-item-last {
  margin-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -2rem;
  top: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #dee2e6;
}

.timeline-marker-primary {
  background-color: #0d6efd;
  color: white;
}

.timeline-marker-success {
  background-color: #198754;
  color: white;
}

.timeline-marker-warning {
  background-color: #ffc107;
  color: #000;
}

.timeline-marker-danger {
  background-color: #dc3545;
  color: white;
}

.timeline-marker-info {
  background-color: #0dcaf0;
  color: #000;
}

.timeline-marker-secondary {
  background-color: #6c757d;
  color: white;
}

.timeline-content {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  padding: 1rem;
  margin-left: 1rem;
}

.timeline-header h6 {
  margin-bottom: 0.5rem;
}

.timeline-body {
  color: #495057;
}

.timeline-changes {
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.75rem;
}

.table-sm th,
.table-sm td {
  padding: 0.25rem 0.5rem;
}

.modal-xl {
  max-width: 1200px;
}
</style>
