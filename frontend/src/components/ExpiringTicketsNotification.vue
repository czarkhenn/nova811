<template>
  <div v-if="visibleNotifications.length > 0" class="expiring-tickets-notifications">
    <div
      v-for="ticket in visibleNotifications"
      :key="ticket.id"
      class="alert alert-warning alert-dismissible fade show notification-item"
      role="alert"
    >
      <div class="d-flex align-items-center justify-content-between">
        <div class="notification-content">
          <div class="d-flex align-items-center">
            <i class="bi bi-exclamation-triangle-fill me-2 text-warning"></i>
            <div>
              <strong>{{ ticket.ticket_number }}</strong> - {{ ticket.organization }}
              <div class="small text-muted">
                <i class="bi bi-clock me-1"></i>
                Expires: {{ formatExpirationDate(ticket.expiration_date) }}
                <span class="ms-2">
                  <i class="bi bi-geo-alt me-1"></i>
                  {{ ticket.location }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="notification-actions d-flex align-items-center">
          <button
            type="button"
            class="btn btn-sm btn-outline-primary me-2"
            @click="viewTicket(ticket)"
            title="View Ticket"
          >
            <i class="bi bi-eye"></i>
            View
          </button>
          
          <button
            type="button"
            class="btn btn-sm btn-outline-success me-2"
            @click="renewTicket(ticket)"
            title="Renew Ticket"
            :disabled="renewingTickets.has(ticket.id)"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'spin': renewingTickets.has(ticket.id) }"></i>
            {{ renewingTickets.has(ticket.id) ? 'Renewing...' : 'Renew' }}
          </button>
          
          <button
            type="button"
            class="btn-close"
            @click="dismissNotification(ticket.id)"
            aria-label="Close"
            title="Dismiss notification"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useTicketsStore } from '@/stores/tickets.js'
import { useToast } from 'vue-toastification'

const ticketsStore = useTicketsStore()
const toast = useToast()

const renewingTickets = ref(new Set())

// Get dismissed notifications from localStorage
const getDismissedNotifications = () => {
  try {
    const dismissed = localStorage.getItem('dismissedTicketNotifications')
    return dismissed ? JSON.parse(dismissed) : {}
  } catch {
    return {}
  }
}

// Save dismissed notifications to localStorage
const saveDismissedNotifications = (dismissed) => {
  try {
    localStorage.setItem('dismissedTicketNotifications', JSON.stringify(dismissed))
  } catch (error) {
    console.warn('Failed to save dismissed notifications:', error)
  }
}

// Computed property for visible notifications (not dismissed)
const visibleNotifications = computed(() => {
  const dismissed = getDismissedNotifications()
  return ticketsStore.expiringTickets.filter(ticket => {
    // Don't show if manually dismissed and ticket hasn't been updated since dismissal
    const dismissedAt = dismissed[ticket.id]
    if (dismissedAt) {
      const ticketUpdatedAt = new Date(ticket.updated_at).getTime()
      const dismissedTime = new Date(dismissedAt).getTime()
      return ticketUpdatedAt > dismissedTime
    }
    return true
  })
})

// Format expiration date for display
const formatExpirationDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

  if (diffMs < 0) {
    return `Expired ${Math.abs(diffHours)}h ago`
  } else if (diffHours < 1) {
    return `${diffMinutes}m remaining`
  } else if (diffHours < 24) {
    return `${diffHours}h ${diffMinutes}m remaining`
  } else {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
}

// View ticket details
const viewTicket = (ticket) => {
  ticketsStore.selectTicket(ticket)
}

// Renew ticket
const renewTicket = async (ticket) => {
  try {
    renewingTickets.value.add(ticket.id)
    await ticketsStore.renewTicket(ticket, 15)
    // Refresh expiring tickets after renewal
    await ticketsStore.loadExpiringTickets()
  } catch (error) {
    toast.error('Failed to renew ticket')
  } finally {
    renewingTickets.value.delete(ticket.id)
  }
}

// Dismiss notification
const dismissNotification = (ticketId) => {
  const dismissed = getDismissedNotifications()
  dismissed[ticketId] = new Date().toISOString()
  saveDismissedNotifications(dismissed)
}

// Auto-refresh interval
let refreshInterval = null

onMounted(() => {
  // Load expiring tickets immediately
  ticketsStore.loadExpiringTickets()
  
  // Set up auto-refresh every 5 minutes
  refreshInterval = setInterval(() => {
    ticketsStore.loadExpiringTickets()
  }, 5 * 60 * 1000) // 5 minutes
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.expiring-tickets-notifications {
  position: fixed;
  top: 56px; /* Below navbar */
  left: 0;
  right: 0;
  z-index: 1040;
  max-height: 50vh;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(5px);
  border-bottom: 1px solid #dee2e6;
}

.notification-item {
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
  animation: slideDown 0.3s ease-out;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-actions {
  flex-shrink: 0;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spin {
  animation: spin 1s linear infinite;
}

/* Responsive design */
@media (max-width: 768px) {
  .notification-actions {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .notification-actions .btn {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
  
  .notification-content .small {
    font-size: 0.7rem;
  }
}

@media (max-width: 576px) {
  .notification-item {
    padding: 0.5rem;
  }
  
  .notification-actions {
    margin-top: 0.5rem;
    align-self: stretch;
  }
  
  .d-flex.align-items-center.justify-content-between {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
