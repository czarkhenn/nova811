<template>
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-ticket-perforated me-2"></i>
            {{ isEdit ? 'Edit Ticket' : 'Create New Ticket' }}
          </h5>
          <button type="button" class="btn-close" @click="$emit('close')"></button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <div class="row g-3">
              <!-- Organization -->
              <div class="col-12">
                <label for="organization" class="form-label">
                  Organization <span class="text-danger">*</span>
                </label>
                <input
                  type="text"
                  class="form-control"
                  id="organization"
                  v-model="form.organization"
                  :class="{ 'is-invalid': errors.organization }"
                  required
                >
                <div v-if="errors.organization" class="invalid-feedback">
                  {{ errors.organization }}
                </div>
              </div>

              <!-- Location -->
              <div class="col-12">
                <label for="location" class="form-label">
                  Location <span class="text-danger">*</span>
                </label>
                <input
                  type="text"
                  class="form-control"
                  id="location"
                  v-model="form.location"
                  :class="{ 'is-invalid': errors.location }"
                  required
                >
                <div v-if="errors.location" class="invalid-feedback">
                  {{ errors.location }}
                </div>
              </div>

              <!-- Status (only for edit) -->
              <div v-if="isEdit" class="col-md-6">
                <label for="status" class="form-label">Status</label>
                <select
                  class="form-select"
                  id="status"
                  v-model="form.status"
                  :class="{ 'is-invalid': errors.status }"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="closed">Closed</option>
                </select>
                <div v-if="errors.status" class="invalid-feedback">
                  {{ errors.status }}
                </div>
              </div>

              <!-- Assigned Contractor -->
              <div :class="isEdit ? 'col-md-6' : 'col-12'">
                <label for="assigned_contractor" class="form-label">
                  Assigned Contractor <span class="text-danger">*</span>
                </label>
                <select
                  class="form-select"
                  id="assigned_contractor"
                  v-model="form.assigned_contractor_id"
                  :class="{ 'is-invalid': errors.assigned_contractor_id }"
                  required
                >
                  <option value="">Select a contractor...</option>
                  <option 
                    v-for="contractor in contractors" 
                    :key="contractor.id" 
                    :value="contractor.id"
                  >
                    {{ contractor.full_name }} ({{ contractor.email }})
                  </option>
                </select>
                <div v-if="errors.assigned_contractor_id" class="invalid-feedback">
                  {{ errors.assigned_contractor_id }}
                </div>
              </div>

              <!-- Expiration Date -->
              <div class="col-md-6">
                <label for="expiration_date" class="form-label">
                  Expiration Date <span class="text-danger">*</span>
                </label>
                <input
                  type="datetime-local"
                  class="form-control"
                  id="expiration_date"
                  v-model="form.expiration_date"
                  :class="{ 'is-invalid': errors.expiration_date }"
                  :min="minDateTime"
                  required
                >
                <div v-if="errors.expiration_date" class="invalid-feedback">
                  {{ errors.expiration_date }}
                </div>
              </div>

              <!-- Quick Expiration Buttons -->
              <div class="col-md-6">
                <label class="form-label">Quick Set Expiration</label>
                <div class="btn-group w-100" role="group">
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary btn-sm"
                    @click="setExpirationDays(7)"
                  >
                    7 Days
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary btn-sm"
                    @click="setExpirationDays(15)"
                  >
                    15 Days
                  </button>
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary btn-sm"
                    @click="setExpirationDays(30)"
                  >
                    30 Days
                  </button>
                </div>
              </div>

              <!-- Notes -->
              <div class="col-12">
                <label for="notes" class="form-label">Notes</label>
                <textarea
                  class="form-control"
                  id="notes"
                  rows="4"
                  v-model="form.notes"
                  :class="{ 'is-invalid': errors.notes }"
                  placeholder="Additional notes and details..."
                ></textarea>
                <div v-if="errors.notes" class="invalid-feedback">
                  {{ errors.notes }}
                </div>
              </div>
            </div>

            <!-- Validation Summary -->
            <div v-if="Object.keys(errors).length > 0" class="alert alert-danger mt-3">
              <h6 class="alert-heading">Please fix the following errors:</h6>
              <ul class="mb-0">
                <li v-for="(error, field) in errors" :key="field">
                  {{ error }}
                </li>
              </ul>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="$emit('close')">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ isEdit ? 'Update Ticket' : 'Create Ticket' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'

const toast = useToast()

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

// Emits
const emit = defineEmits(['close', 'save'])

// Reactive data
const loading = ref(false)
const errors = ref({})

const form = ref({
  organization: '',
  location: '',
  status: 'open',
  assigned_contractor_id: '',
  expiration_date: '',
  notes: ''
})

// Computed
const isEdit = computed(() => !!props.ticket)

const minDateTime = computed(() => {
  const now = new Date()
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
  return now.toISOString().slice(0, 16)
})

// Methods
const initializeForm = () => {
  if (props.ticket) {
    // Edit mode - populate form with ticket data
    form.value = {
      organization: props.ticket.organization || '',
      location: props.ticket.location || '',
      status: props.ticket.status || 'open',
      assigned_contractor_id: props.ticket.assigned_contractor?.id || '',
      expiration_date: formatDateTimeLocal(props.ticket.expiration_date) || '',
      notes: props.ticket.notes || ''
    }
  } else {
    // Create mode - set defaults
    form.value = {
      organization: '',
      location: '',
      status: 'open',
      assigned_contractor_id: '',
      expiration_date: '',
      notes: ''
    }
    
    // Set default expiration to 15 days from now
    setExpirationDays(15)
  }
  
  // Clear errors
  errors.value = {}
}

const formatDateTimeLocal = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
}

const setExpirationDays = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  form.value.expiration_date = date.toISOString().slice(0, 16)
  
  // Show toast notification
  toast.success(`Expiration date set to ${days} days!`)
}

const validateForm = () => {
  errors.value = {}
  
  if (!form.value.organization.trim()) {
    errors.value.organization = 'Organization is required'
  }
  
  if (!form.value.location.trim()) {
    errors.value.location = 'Location is required'
  }
  
  if (!form.value.assigned_contractor_id) {
    errors.value.assigned_contractor_id = 'Assigned contractor is required'
  }
  
  if (!form.value.expiration_date) {
    errors.value.expiration_date = 'Expiration date is required'
  } else {
    const expirationDate = new Date(form.value.expiration_date)
    const now = new Date()
    
    if (expirationDate <= now) {
      errors.value.expiration_date = 'Expiration date must be in the future'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = () => {
  if (!validateForm()) {
    return
  }
  
  // Prepare data for API
  const ticketData = {
    organization: form.value.organization.trim(),
    location: form.value.location.trim(),
    assigned_contractor_id: form.value.assigned_contractor_id,
    expiration_date: new Date(form.value.expiration_date).toISOString(),
    notes: form.value.notes.trim()
  }
  
  // Add status for edit mode
  if (isEdit.value) {
    ticketData.status = form.value.status
  }
  
  // Emit save event - let parent handle the API call and loading
  emit('save', ticketData)
}

// Watch for prop changes
watch(() => props.show, (newValue) => {
  if (newValue) {
    initializeForm()
  }
})

watch(() => props.ticket, () => {
  if (props.show) {
    initializeForm()
  }
})

// Lifecycle
onMounted(() => {
  if (props.show) {
    initializeForm()
  }
})
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

.form-control:focus,
.form-select:focus {
  border-color: #86b7fe;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.btn-group .btn {
  flex: 1;
}

.alert ul {
  padding-left: 1.5rem;
}
</style>
