<template>
  <div class="modal fade" id="assignTicketModal" tabindex="-1" aria-labelledby="assignTicketModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="assignTicketModalLabel">
            <i class="bi bi-person-plus me-2"></i>
            Assign Ticket
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
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
                  <span :class="getStatusBadgeClass(ticket.status)">
                    {{ ticket.status }}
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
                v-model="form.assigned_contractor" 
                class="form-select"
                :class="{ 'is-invalid': errors.assigned_contractor }"
                required
              >
                <option value="">Select a contractor...</option>
                <option 
                  v-for="contractor in contractors" 
                  :key="contractor.id" 
                  :value="contractor.id"
                >
                  {{ contractor.first_name }} {{ contractor.last_name }} ({{ contractor.email }})
                </option>
              </select>
              <div v-if="errors.assigned_contractor" class="invalid-feedback">
                {{ errors.assigned_contractor }}
              </div>
            </div>

            <div class="mb-3">
              <label for="assignmentNotes" class="form-label">
                <i class="bi bi-chat-text me-1"></i>
                Assignment Notes
              </label>
              <textarea 
                id="assignmentNotes" 
                v-model="form.notes" 
                class="form-control"
                :class="{ 'is-invalid': errors.notes }"
                rows="3"
                placeholder="Add any notes about this assignment..."
              ></textarea>
              <div v-if="errors.notes" class="invalid-feedback">
                {{ errors.notes }}
              </div>
              <div class="form-text">
                Optional notes will be added to the ticket's activity log.
              </div>
            </div>

            <div v-if="ticket?.assigned_contractor" class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Current Assignment:</strong> 
              {{ ticket.assigned_contractor.first_name }} {{ ticket.assigned_contractor.last_name }}
              ({{ ticket.assigned_contractor.email }})
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="bi bi-x-circle me-1"></i>
            Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="handleAssign"
            :disabled="loading || !form.assigned_contractor"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <i v-else class="bi bi-person-check me-1"></i>
            {{ loading ? 'Assigning...' : 'Assign Ticket' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

export default {
  name: 'AssignTicketModal',
  props: {
    ticket: {
      type: Object,
      default: null
    }
  },
  emits: ['ticket-assigned'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const loading = ref(false)
    const contractors = ref([])
    const errors = reactive({})

    const form = reactive({
      assigned_contractor: '',
      notes: ''
    })

    // Reset form when ticket changes
    watch(() => props.ticket, (newTicket) => {
      if (newTicket) {
        form.assigned_contractor = newTicket.assigned_contractor?.id || ''
        form.notes = ''
        clearErrors()
      }
    })

    const clearErrors = () => {
      Object.keys(errors).forEach(key => {
        delete errors[key]
      })
    }

    const loadContractors = async () => {
      try {
        const response = await api.get('/users/', {
          params: { role: 'contractor' }
        })
        contractors.value = response.data.results || response.data
      } catch (error) {
        console.error('Error loading contractors:', error)
      }
    }

    const validateForm = () => {
      clearErrors()
      let isValid = true

      if (!form.assigned_contractor) {
        errors.assigned_contractor = 'Please select a contractor'
        isValid = false
      }

      if (form.notes && form.notes.length > 500) {
        errors.notes = 'Notes cannot exceed 500 characters'
        isValid = false
      }

      return isValid
    }

    const handleAssign = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      clearErrors()

      try {
        const payload = {
          assigned_contractor: form.assigned_contractor
        }

        if (form.notes.trim()) {
          payload.notes = form.notes.trim()
        }

        const response = await api.post(`/tickets/${props.ticket.id}/assign/`, payload)
        
        emit('ticket-assigned', response.data)
        
        // Close modal
        const modal = document.getElementById('assignTicketModal')
        const bsModal = window.bootstrap.Modal.getInstance(modal)
        if (bsModal) {
          bsModal.hide()
        }

        // Reset form
        form.assigned_contractor = ''
        form.notes = ''

      } catch (error) {
        console.error('Error assigning ticket:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          if (typeof errorData === 'object') {
            Object.keys(errorData).forEach(key => {
              if (key in form) {
                errors[key] = Array.isArray(errorData[key]) 
                  ? errorData[key][0] 
                  : errorData[key]
              }
            })
          } else {
            errors.general = 'Failed to assign ticket. Please try again.'
          }
        } else {
          errors.general = 'Network error. Please check your connection and try again.'
        }
      } finally {
        loading.value = false
      }
    }

    const getStatusBadgeClass = (status) => {
      const statusClasses = {
        'open': 'badge bg-success',
        'in_progress': 'badge bg-warning text-dark',
        'pending': 'badge bg-info',
        'closed': 'badge bg-secondary',
        'expired': 'badge bg-danger'
      }
      return statusClasses[status] || 'badge bg-secondary'
    }

    // Load contractors when component mounts
    loadContractors()

    return {
      loading,
      contractors,
      form,
      errors,
      handleAssign,
      getStatusBadgeClass,
      clearErrors
    }
  }
}
</script>

<style scoped>
.modal-body {
  max-height: 70vh;
  overflow-y: auto;
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

.form-text {
  font-size: 0.875em;
  color: #6c757d;
}
</style>
