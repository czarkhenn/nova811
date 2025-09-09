<template>
  <div class="app-layout">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold" href="#">
          <i class="bi bi-shield-check me-2"></i>
          Nova811
        </a>

        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link to="/dashboard" class="nav-link" active-class="active">
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/tickets" class="nav-link" active-class="active">
                <i class="bi bi-ticket-perforated me-1"></i>
                Tickets
              </router-link>
            </li>
            <li class="nav-item">
              <router-link to="/logs" class="nav-link" active-class="active">
                <i class="bi bi-journal-text me-1"></i>
                Activity Logs
              </router-link>
            </li>
          </ul>

          <div class="dropdown">
            <button
              class="btn btn-outline-light dropdown-toggle"
              type="button"
              id="userDropdown"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-person-circle me-1"></i>
              {{ authStore.user?.first_name }} {{ authStore.user?.last_name }}
            </button>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
              <li>
                <router-link to="/profile" class="dropdown-item">
                  <i class="bi bi-person me-2"></i>
                  Profile
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <button class="dropdown-item text-danger" @click="handleLogout">
                  <i class="bi bi-box-arrow-right me-2"></i>
                  Logout
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>


    <main class="main-content">
      <div class="container-fluid py-4">
        <slot />
      </div>
    </main>

    <!-- Global Ticket Modals -->
    <TicketDetailModal 
      v-if="ticketsStore.showDetailModal && ticketsStore.selectedTicket"
      :show="ticketsStore.showDetailModal"
      :ticket="ticketsStore.selectedTicket"
      @close="ticketsStore.closeDetailModal"
      @edit="ticketsStore.openEditModal"
      @renew="handleRenewTicket"
      @close-ticket="handleCloseTicket"
      @assign="(ticket) => ticketsStore.openAssignModal(ticket, authStore.user?.role)"
    />
    
    <AssignTicketModal 
      v-if="ticketsStore.showAssignModal && ticketsStore.selectedTicket"
      :show="ticketsStore.showAssignModal"
      :ticket="ticketsStore.selectedTicket"
      @close="ticketsStore.closeAssignModal"
    />
    
    <AuditTrailModal 
      v-if="ticketsStore.showAuditTrailModal && ticketsStore.selectedTicket"
      :show="ticketsStore.showAuditTrailModal"
      :ticket="ticketsStore.selectedTicket"
      @close="ticketsStore.closeAuditTrailModal"
    />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import { useTicketsStore } from '@/stores/tickets.js'
import { useToast } from 'vue-toastification'
import TicketDetailModal from './TicketDetailModal.vue'
import AssignTicketModal from './AssignTicketModal.vue'
import AuditTrailModal from './AuditTrailModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const ticketsStore = useTicketsStore()
const toast = useToast()

const handleLogout = () => {
  authStore.logout()
  toast.success('Logged out successfully')
  router.push('/login')
}

const handleRenewTicket = async (ticket) => {
  try {
    await ticketsStore.renewTicket(ticket, 15)
    ticketsStore.closeDetailModal()
  } catch (error) {
    // Error handling is done in the store
  }
}

const handleCloseTicket = async (ticket) => {
  try {
    await ticketsStore.closeTicket(ticket)
    ticketsStore.closeDetailModal()
  } catch (error) {
    // Error handling is done in the store
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.main-content {
  margin-top: 56px;
  min-height: calc(100vh - 56px);
  background-color: #f8f9fa;
}

.navbar-brand {
  font-size: 1.5rem;
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
}

.dropdown-menu {
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>
