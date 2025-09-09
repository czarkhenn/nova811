<template>
  <div class="ticket-card border-bottom">
    <div class="row align-items-center p-3">
      <!-- Ticket Info -->
      <div class="col-md-6">
        <div class="d-flex align-items-start">
          <div class="me-3">
            <div class="ticket-status-indicator" :class="statusClass"></div>
          </div>
          <div class="flex-grow-1">
            <h6 class="mb-1">
              <span class="text-primary fw-bold">{{ ticket.ticket_number }}</span>
              <span class="badge ms-2" :class="statusBadgeClass">
                {{ ticket.status_display }}
              </span>
            </h6>
            <h5 class="mb-2">{{ ticket.organization }}</h5>
            <p class="text-muted mb-1">
              <i class="bi bi-geo-alt me-1"></i>
              {{ ticket.location }}
            </p>
            <div class="d-flex align-items-center text-muted small">
              <span class="me-3">
                <i class="bi bi-person me-1"></i>
                {{ ticket.assigned_contractor.first_name }} {{ ticket.assigned_contractor.last_name }}
              </span>
              <span class="me-3">
                <i class="bi bi-calendar me-1"></i>
                {{ formatDate(ticket.created_date) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Expiration Info -->
      <div class="col-md-3">
        <div class="text-center">
          <div class="expiration-status" :class="expirationClass">
            <i :class="expirationIcon" class="display-6 mb-2"></i>
            <h6 class="mb-1">{{ expirationStatus }}</h6>
            <small class="text-muted">
              {{ formatDate(ticket.expiration_date) }}
            </small>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="col-md-3">
        <div class="d-flex justify-content-end">
          <div class="btn-group" role="group">
            <button 
              class="btn btn-outline-primary btn-sm"
              @click="$emit('view', ticket)"
              title="View Details"
            >
              <i class="bi bi-eye"></i>
            </button>
            
            <button 
              v-if="canEdit"
              class="btn btn-outline-secondary btn-sm"
              @click="$emit('edit', ticket)"
              title="Edit Ticket"
            >
              <i class="bi bi-pencil"></i>
            </button>
            
            <div class="btn-group" role="group">
              <button 
                class="btn btn-outline-info btn-sm dropdown-toggle"
                data-bs-toggle="dropdown"
                title="Actions"
              >
                <i class="bi bi-three-dots"></i>
              </button>
              <ul class="dropdown-menu">
                <li v-if="canRenew">
                  <a 
                    class="dropdown-item"
                    href="#"
                    @click.prevent="$emit('renew', ticket)"
                  >
                    <i class="bi bi-arrow-clockwise me-2"></i>
                    Renew (+15 days)
                  </a>
                </li>
                <li v-if="authStore.isAdmin">
                  <a 
                    class="dropdown-item"
                    href="#"
                    @click.prevent="$emit('assign', ticket)"
                  >
                    <i class="bi bi-person-plus me-2"></i>
                    Reassign
                  </a>
                </li>
                <li v-if="canClose">
                  <hr class="dropdown-divider">
                  <a 
                    class="dropdown-item text-danger"
                    href="#"
                    @click.prevent="$emit('close', ticket)"
                  >
                    <i class="bi bi-x-circle me-2"></i>
                    Close Ticket
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Notes Preview (if exists) -->
    <div v-if="ticket.notes" class="px-3 pb-3">
      <div class="notes-preview">
        <small class="text-muted">
          <i class="bi bi-chat-text me-1"></i>
          {{ truncateNotes(ticket.notes) }}
        </small>
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
  ticket: {
    type: Object,
    required: true
  }
})

// Emits
defineEmits(['view', 'edit', 'renew', 'close', 'assign'])

// Computed properties
const statusClass = computed(() => {
  const classes = {
    'open': 'bg-success',
    'in_progress': 'bg-warning',
    'closed': 'bg-secondary'
  }
  return classes[props.ticket.status] || 'bg-secondary'
})

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
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const truncateNotes = (notes) => {
  if (!notes) return ''
  return notes.length > 100 ? notes.substring(0, 100) + '...' : notes
}
</script>

<style scoped>
.ticket-card {
  transition: all 0.2s ease-in-out;
}

.ticket-card:hover {
  background-color: #f8f9fa;
}

.ticket-status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
}

.expiration-status {
  padding: 1rem;
  border-radius: 8px;
  background-color: rgba(0, 0, 0, 0.02);
}

.notes-preview {
  background-color: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  border-left: 3px solid #dee2e6;
}

.btn-group .btn {
  border-radius: 0.25rem;
}

.btn-group .btn:not(:last-child) {
  border-right: none;
}

.btn-group .btn:not(:first-child) {
  border-left: none;
}

.dropdown-menu {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>
