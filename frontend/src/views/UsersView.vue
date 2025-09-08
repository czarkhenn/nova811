<template>
  <AppLayout>
    <div class="users">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col">
                  <h1 class="h3 mb-1">
                    <i class="bi bi-people me-2"></i>
                    User Management
                  </h1>
                  <p class="mb-0 text-muted">
                    Manage system users and their permissions
                  </p>
                </div>
                <div class="col-auto">
                  <button class="btn btn-primary" @click="showCreateModal = true">
                    <i class="bi bi-person-plus me-1"></i>
                    Add User
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="row">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white">
              <h5 class="card-title mb-0">
                <i class="bi bi-table me-2"></i>
                All Users
              </h5>
            </div>
            <div class="card-body">
              <div v-if="isLoading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2 text-muted">Loading users...</p>
              </div>

              <div v-else-if="users.length === 0" class="text-center py-4">
                <i class="bi bi-people display-4 text-muted"></i>
                <p class="mt-2 text-muted">No users found</p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Joined</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id">
                      <td>
                        <div class="d-flex align-items-center">
                          <i class="bi bi-person-circle fs-4 text-primary me-2"></i>
                          <div>
                            <div class="fw-semibold">{{ user.first_name }} {{ user.last_name }}</div>
                            <small class="text-muted">ID: {{ user.id }}</small>
                          </div>
                        </div>
                      </td>
                      <td>{{ user.email }}</td>
                      <td>
                        <span class="badge" :class="user.role === 'admin' ? 'bg-danger' : 'bg-primary'">
                          {{ user.role === 'admin' ? 'Administrator' : 'Contractor' }}
                        </span>
                      </td>
                      <td>
                        <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-secondary'">
                          {{ user.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                      <td>{{ formatDate(user.date_joined) }}</td>
                      <td>
                        <div class="btn-group btn-group-sm" role="group">
                          <button
                            class="btn btn-outline-primary"
                            @click="editUser(user)"
                            :title="`Edit ${user.first_name}`"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button
                            v-if="user.is_active"
                            class="btn btn-outline-warning"
                            @click="toggleUserStatus(user, false)"
                            :title="`Deactivate ${user.first_name}`"
                          >
                            <i class="bi bi-person-dash"></i>
                          </button>
                          <button
                            v-else
                            class="btn btn-outline-success"
                            @click="toggleUserStatus(user, true)"
                            :title="`Activate ${user.first_name}`"
                          >
                            <i class="bi bi-person-check"></i>
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
    </div>

    <!-- Create/Edit User Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" :style="{ display: showCreateModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-person-plus me-2"></i>
              {{ editingUser ? 'Edit User' : 'Add New User' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="modalFirstName" class="form-label">First Name</label>
                  <input
                    id="modalFirstName"
                    v-model="userForm.firstName"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': modalErrors.firstName }"
                    required
                  />
                  <div v-if="modalErrors.firstName" class="invalid-feedback">
                    {{ modalErrors.firstName }}
                  </div>
                </div>
                <div class="col-md-6 mb-3">
                  <label for="modalLastName" class="form-label">Last Name</label>
                  <input
                    id="modalLastName"
                    v-model="userForm.lastName"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': modalErrors.lastName }"
                    required
                  />
                  <div v-if="modalErrors.lastName" class="invalid-feedback">
                    {{ modalErrors.lastName }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="modalEmail" class="form-label">Email</label>
                <input
                  id="modalEmail"
                  v-model="userForm.email"
                  type="email"
                  class="form-control"
                  :class="{ 'is-invalid': modalErrors.email }"
                  required
                />
                <div v-if="modalErrors.email" class="invalid-feedback">
                  {{ modalErrors.email }}
                </div>
              </div>

              <div class="mb-3">
                <label for="modalPhoneNumber" class="form-label">Phone Number</label>
                <input
                  id="modalPhoneNumber"
                  v-model="userForm.phoneNumber"
                  type="tel"
                  class="form-control"
                  :class="{ 'is-invalid': modalErrors.phoneNumber }"
                />
                <div v-if="modalErrors.phoneNumber" class="invalid-feedback">
                  {{ modalErrors.phoneNumber }}
                </div>
              </div>

              <div class="mb-3">
                <label for="modalRole" class="form-label">Role</label>
                <select
                  id="modalRole"
                  v-model="userForm.role"
                  class="form-select"
                  :class="{ 'is-invalid': modalErrors.role }"
                  required
                >
                  <option value="contractor">Contractor</option>
                  <option value="admin">Administrator</option>
                </select>
                <div v-if="modalErrors.role" class="invalid-feedback">
                  {{ modalErrors.role }}
                </div>
              </div>

              <div v-if="!editingUser" class="mb-3">
                <label for="modalPassword" class="form-label">Password</label>
                <input
                  id="modalPassword"
                  v-model="userForm.password"
                  type="password"
                  class="form-control"
                  :class="{ 'is-invalid': modalErrors.password }"
                  required
                />
                <div v-if="modalErrors.password" class="invalid-feedback">
                  {{ modalErrors.password }}
                </div>
                <div class="form-text">
                  Password must be at least 8 characters long
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="handleSubmit"
              :disabled="isSubmitting"
            >
              <span
                v-if="isSubmitting"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ isSubmitting ? 'Saving...' : (editingUser ? 'Update User' : 'Create User') }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showCreateModal" class="modal-backdrop fade show"></div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api.js'

const toast = useToast()

const users = ref([])
const isLoading = ref(false)
const showCreateModal = ref(false)
const editingUser = ref(null)
const isSubmitting = ref(false)

const userForm = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phoneNumber: '',
  role: 'contractor',
  password: '',
})

const modalErrors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  phoneNumber: '',
  role: '',
  password: '',
})

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/users/')
    users.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    console.error('Failed to fetch users:', error)
    toast.error('Failed to load users')
    users.value = []
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  userForm.firstName = ''
  userForm.lastName = ''
  userForm.email = ''
  userForm.phoneNumber = ''
  userForm.role = 'contractor'
  userForm.password = ''
  
  Object.keys(modalErrors).forEach(key => {
    modalErrors[key] = ''
  })
}

const closeModal = () => {
  showCreateModal.value = false
  editingUser.value = null
  resetForm()
}

const editUser = (user) => {
  editingUser.value = user
  userForm.firstName = user.first_name
  userForm.lastName = user.last_name
  userForm.email = user.email
  userForm.phoneNumber = user.phone_number || ''
  userForm.role = user.role
  showCreateModal.value = true
}

const validateForm = () => {
  Object.keys(modalErrors).forEach(key => {
    modalErrors[key] = ''
  })

  let isValid = true

  if (!userForm.firstName.trim()) {
    modalErrors.firstName = 'First name is required'
    isValid = false
  }

  if (!userForm.lastName.trim()) {
    modalErrors.lastName = 'Last name is required'
    isValid = false
  }

  if (!userForm.email) {
    modalErrors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userForm.email)) {
    modalErrors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (!editingUser.value && !userForm.password) {
    modalErrors.password = 'Password is required'
    isValid = false
  } else if (!editingUser.value && userForm.password.length < 8) {
    modalErrors.password = 'Password must be at least 8 characters long'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) return

  isSubmitting.value = true

  try {
    if (editingUser.value) {
      // Update existing user
      const response = await api.patch(`/users/${editingUser.value.id}/`, {
        first_name: userForm.firstName.trim(),
        last_name: userForm.lastName.trim(),
        email: userForm.email.trim(),
        phone_number: userForm.phoneNumber.trim(),
      })
      
      // Update role if changed
      if (userForm.role !== editingUser.value.role) {
        await api.post(`/users/${editingUser.value.id}/role/`, {
          role: userForm.role
        })
      }

      toast.success('User updated successfully!')
    } else {
      // Create new user
      await api.post('/users/create/', {
        first_name: userForm.firstName.trim(),
        last_name: userForm.lastName.trim(),
        email: userForm.email.trim(),
        phone_number: userForm.phoneNumber.trim(),
        role: userForm.role,
        password: userForm.password,
      })

      toast.success('User created successfully!')
    }

    closeModal()
    await fetchUsers()
  } catch (error) {
    console.error('Failed to save user:', error)
    toast.error('Failed to save user. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

const toggleUserStatus = async (user, activate) => {
  try {
    const endpoint = activate ? 'activate' : 'deactivate'
    await api.post(`/users/${user.id}/${endpoint}/`)
    
    toast.success(`User ${activate ? 'activated' : 'deactivated'} successfully!`)
    await fetchUsers()
  } catch (error) {
    console.error('Failed to toggle user status:', error)
    toast.error('Failed to update user status')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users {
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

.table th {
  border-top: none;
  font-weight: 600;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>
