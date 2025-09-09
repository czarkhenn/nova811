<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-person-plus me-2"></i>
            Reassign Ticket
          </h5>
          <button type="button" class="btn-close" @click="ticketsStore.closeAssignModal()"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="ticket" class="mb-3">
            <div class="card bg-light">
              <div class="card-body py-2">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{{ ticket.ticket_number }}</strong>
                    <span class="text-muted ms-2">{{ ticket.organization }}</span>
                  </div>
                  <span class="badge" :class="getStatusBadgeClass(ticket.status)">
                    {{ ticket.status_display || ticket.status }}
                  </span>
                </div>
                <small class="text-muted">{{ ticket.location }}</small>
              </div>
            </div>
          </div>

          <form @submit.prevent="handleAssign">
            <div class="mb-3">
              <label for="assignedContractor" class="form-label">
                <i class="bi bi-person me-1"></i>
                Assign to Contractor <span class="text-danger">*</span>
              </label>
              <select 
                id="assignedContractor" 
                v-model="selectedContractorId" 
                class="form-select"
                :class="{ 'is-invalid': errors.assigned_contractor }"
                required
              >
                <option value="">Select a contractor...</option>
                <option 
                  v-for="contractor in availableContractors" 
                  :key="contractor.id" 
                  :value="contractor.id"
                >
                  {{ contractor.first_name }} {{ contractor.last_name }} ({{ contractor.email }})
                </option>
              </select>
              <div v-if="contractorsLoading" class="form-text">
                <i class="bi bi-hourglass-split me-1"></i>
                Loading contractors...
              </div>
              <div v-else-if="availableContractors.length === 0" class="form-text text-warning">
                <i class="bi bi-exclamation-triangle me-1"></i>
                No contractors available
              </div>
              <div v-if="errors.assigned_contractor" class="invalid-feedback">
                {{ errors.assigned_contractor }}
              </div>
            </div>

            <div v-if="ticket?.assigned_contractor" class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Current Assignment:</strong> 
              {{ ticket.assigned_contractor.first_name }} {{ ticket.assigned_contractor.last_name }}
              ({{ ticket.assigned_contractor.email }})
            </div>

            <div v-if="errors.general || ticketsStore.assignmentError" class="alert alert-danger">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ errors.general || ticketsStore.assignmentError }}
            </div>
          </form>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="ticketsStore.closeAssignModal()">
            <i class="bi bi-x-circle me-1"></i>
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="handleAssign"
            :disabled="ticketsStore.assignmentLoading || !selectedContractorId"
          >
            <span v-if="ticketsStore.assignmentLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-person-check me-1"></i>
            {{ ticketsStore.assignmentLoading ? 'Assigning...' : 'Reassign Ticket' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useTicketsStore } from '@/stores/tickets.js'
import { useAuthStore } from '@/stores/auth.js'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  ticket: {
    type: Object,
    default: null
  },
  contractors: {
    type: Array,
    default: () => []
  }
})

// Store
const ticketsStore = useTicketsStore()
const authStore = useAuthStore()

// Reactive data
const selectedContractorId = ref('')
const errors = ref({})
const contractorsLoading = ref(false)

// Methods
const clearErrors = () => {
  errors.value = {}
}

// Ensure contractors are loaded when modal opens
const ensureContractorsLoaded = async () => {
  if (authStore.isAdmin && (!props.contractors || props.contractors.length === 0)) {
    contractorsLoading.value = true
    try {
      await ticketsStore.loadContractors()
    } catch (error) {
      console.error('Failed to load contractors:', error)
    } finally {
      contractorsLoading.value = false
    }
  }
}

// Watch for modal show changes to load contractors
watch(() => props.show, (isShowing) => {
  if (isShowing) {
    ensureContractorsLoaded()
  }
}, { immediate: true })

// Watch for ticket changes to reset form
watch(() => props.ticket, (newTicket) => {
  if (newTicket) {
    selectedContractorId.value = newTicket.assigned_contractor?.id || ''
    clearErrors()
  }
}, { immediate: true })

// Load contractors on mount if needed
onMounted(() => {
  if (props.show) {
    ensureContractorsLoaded()
  }
})

// Computed property to get contractors from either props or store
const availableContractors = computed(() => {
  // Use contractors from store if available, otherwise use props
  return ticketsStore.contractors.length > 0 ? ticketsStore.contractors : props.contractors
})

const validateForm = () => {
  clearErrors()
  let isValid = true

  if (!selectedContractorId.value) {
    errors.value.assigned_contractor = 'Please select a contractor'
    isValid = false
  }

  return isValid
}

const handleAssign = async () => {
  if (!validateForm()) {
    return
  }

  clearErrors()

  try {
    // Call the store method directly - it will handle modal closing on success
    await ticketsStore.assignTicket(props.ticket.id, selectedContractorId.value)
    // Don't reset form here - let the modal close naturally
    // The form will be reset when the modal reopens due to the watch
  } catch (error) {
    // Handle any additional errors if needed
    if (ticketsStore.assignmentError) {
      errors.value.general = ticketsStore.assignmentError
    }
  }
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

.card {
  border: 1px solid #dee2e6;
}

.form-select:focus,
.form-control:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.alert {
  border: none;
  border-radius: 0.5rem;
}

.badge {
  font-size: 0.75em;
  padding: 0.35em 0.65em;
  border-radius: 0.375rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.btn:disabled {
  opacity: 0.65;
}

.invalid-feedback {
  display: block;
}
</style>
