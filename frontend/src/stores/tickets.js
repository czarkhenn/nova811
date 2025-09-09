import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useToast } from 'vue-toastification'
import api from '@/services/api.js'

export const useTicketsStore = defineStore('tickets', () => {
  const tickets = ref([])
  const selectedTicket = ref(null)
  const stats = ref(null)
  const contractors = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  // Expiring tickets for notifications
  const expiringTickets = ref([])
  const expiringTicketsLoading = ref(false)
  
  const assignmentLoading = ref(false)
  const assignmentError = ref(null)
  
  const showDetailModal = ref(false)
  const showCreateModal = ref(false)
  const showEditModal = ref(false)
  const showAssignModal = ref(false)
  const showAuditTrailModal = ref(false)
  
  const filters = ref({
    status: '',
    search: '',
    expiring_soon: false,
    expired: false
  })

  const toast = useToast()

  const hasFilters = computed(() => {
    return filters.value.status || 
           filters.value.search || 
           filters.value.expiring_soon || 
           filters.value.expired
  })

  const loadTickets = async () => {
    try {
      loading.value = true
      
      const params = new URLSearchParams()
      if (filters.value.status) params.append('status', filters.value.status)
      if (filters.value.search) params.append('search', filters.value.search)
      if (filters.value.expiring_soon) params.append('expiring_soon', 'true')
      if (filters.value.expired) params.append('expired', 'true')
      
      const response = await api.get(`/tickets/?${params.toString()}`)
      tickets.value = response.data.results || response.data
    } catch (err) {
      toast.error('Failed to load tickets')
      error.value = 'Failed to load tickets'
    } finally {
      loading.value = false
    }
  }

  const loadStats = async () => {
    try {
      const response = await api.get('/tickets/stats/')
      stats.value = response.data
    } catch (err) {
      // Silently handle stats loading error
    }
  }

  const loadContractors = async (userRole = null) => {
    try {
      // Only load contractors for admin users
      if (userRole && userRole !== 'admin') {
        contractors.value = []
        return
      }
      
      const response = await api.get('/tickets/contractors/')
      contractors.value = response.data
    } catch (err) {
      console.error('Failed to load contractors:', err)
      if (err.response?.status === 403) {
        toast.error('You do not have permission to view contractors')
      } else {
        toast.error('Failed to load contractors')
      }
      contractors.value = []
    }
  }

  const loadExpiringTickets = async () => {
    try {
      expiringTicketsLoading.value = true
      
      // Fetch tickets that are expiring soon (within 48 hours)
      const response = await api.get('/tickets/?expiring_soon=true')
      expiringTickets.value = response.data.results || response.data
    } catch (err) {
      // Silently handle expiring tickets loading error
      console.warn('Failed to load expiring tickets:', err)
    } finally {
      expiringTicketsLoading.value = false
    }
  }

  const selectTicket = async (ticket) => {
    try {
      // Fetch detailed ticket data including logs and user details
      const response = await api.get(`/tickets/${ticket.id}/`)
      selectedTicket.value = response.data
      showDetailModal.value = true
    } catch (err) {
      toast.error('Failed to load ticket details')
      // Fallback to basic ticket data if detailed fetch fails
      selectedTicket.value = ticket
      showDetailModal.value = true
    }
  }

  const closeDetailModal = () => {
    showDetailModal.value = false
    selectedTicket.value = null
  }

  const openCreateModal = () => {
    selectedTicket.value = null
    showCreateModal.value = true
  }

  const openEditModal = (ticket) => {
    selectedTicket.value = ticket
    showEditModal.value = true
  }

  const closeModal = () => {
    showCreateModal.value = false
    showEditModal.value = false
    selectedTicket.value = null
  }

  const openAssignModal = async (ticket, userRole = null) => {
    // Don't change selectedTicket if detail modal is open to preserve its state
    if (!showDetailModal.value) {
      selectedTicket.value = ticket
    }
    
    // Clear any previous assignment errors
    assignmentError.value = null
    
    // Ensure contractors are loaded before showing modal (only for admin users)
    if (contractors.value.length === 0) {
      try {
        await loadContractors(userRole)
      } catch (error) {
        console.error('Failed to load contractors for assignment:', error)
      }
    }
    
    showAssignModal.value = true
  }

  const closeAssignModal = () => {
    showAssignModal.value = false
    // Only clear selectedTicket if detail modal is not open
    if (!showDetailModal.value) {
      selectedTicket.value = null
    }
    // Clear assignment errors when closing
    assignmentError.value = null
  }

  const openAuditTrailModal = (ticket) => {
    selectedTicket.value = ticket
    showAuditTrailModal.value = true
  }

  const closeAuditTrailModal = () => {
    showAuditTrailModal.value = false
    selectedTicket.value = null
  }

  const createTicket = async (ticketData) => {
    try {
      const response = await api.post('/tickets/', ticketData)
      toast.success('Ticket created successfully')
      closeModal()
      await Promise.all([loadTickets(), loadStats()])
      return response.data
    } catch (err) {
      if (err.response?.status === 400) {
        const errorData = err.response.data
        if (errorData.error) {
          toast.error(`Validation Error: ${errorData.error}`)
        } else {
          toast.error('Please check your input data and try again')
        }
      } else if (err.response?.status === 403) {
        toast.error('You do not have permission to perform this action')
      } else {
        toast.error('Failed to create ticket. Please try again.')
      }
      throw err
    }
  }

  const updateTicket = async (ticketData) => {
    try {
      const response = await api.put(`/tickets/${selectedTicket.value.id}/`, ticketData)
      toast.success('Ticket updated successfully')
      closeModal()
      await Promise.all([loadTickets(), loadStats()])
      return response.data
    } catch (err) {
      if (err.response?.status === 400) {
        const errorData = err.response.data
        if (errorData.error) {
          toast.error(`Validation Error: ${errorData.error}`)
        } else {
          toast.error('Please check your input data and try again')
        }
      } else if (err.response?.status === 403) {
        toast.error('You do not have permission to perform this action')
      } else if (err.response?.status === 404) {
        toast.error('Ticket not found')
      } else {
        toast.error('Failed to update ticket. Please try again.')
      }
      throw err
    }
  }

  const renewTicket = async (ticket, days = 15) => {
    try {
      await api.post(`/tickets/${ticket.id}/renew/`, { days })
      toast.success(`Ticket renewed for ${days} days`)
      await Promise.all([loadTickets(), loadStats(), loadExpiringTickets()])
    } catch (err) {
      toast.error('Failed to renew ticket')
      throw err
    }
  }

  const closeTicket = async (ticket, reason = '') => {
    try {
      await api.post(`/tickets/${ticket.id}/close/`, { reason })
      toast.success('Ticket closed successfully')
      await Promise.all([loadTickets(), loadStats()])
    } catch (err) {
      toast.error('Failed to close ticket')
    }
  }

  const assignTicket = async (ticketId, contractorId) => {
    try {
      assignmentLoading.value = true
      assignmentError.value = null
      
      await api.post(`/tickets/${ticketId}/assign/`, { 
        assigned_contractor_id: contractorId 
      })
      
      toast.success('Ticket assigned successfully')
      closeAssignModal()
      
      // If detail modal is open, refresh the ticket details to show updated assignment
      if (showDetailModal.value && selectedTicket.value?.id === ticketId) {
        try {
          const response = await api.get(`/tickets/${ticketId}/`)
          selectedTicket.value = response.data
        } catch (err) {
          // Silently handle ticket refresh error
        }
      }
      
      await loadTickets()
    } catch (err) {
      // Set specific error message based on response
      if (err.response?.status === 400) {
        const errorData = err.response.data
        assignmentError.value = errorData.error || 'Invalid assignment data'
        toast.error(`Assignment Error: ${assignmentError.value}`)
      } else if (err.response?.status === 403) {
        assignmentError.value = 'You do not have permission to assign tickets'
        toast.error(assignmentError.value)
      } else if (err.response?.status === 404) {
        assignmentError.value = 'Ticket not found'
        toast.error(assignmentError.value)
      } else {
        assignmentError.value = 'Failed to assign ticket. Please try again.'
        toast.error(assignmentError.value)
      }
    } finally {
      assignmentLoading.value = false
    }
  }

  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      status: '',
      search: '',
      expiring_soon: false,
      expired: false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    tickets,
    selectedTicket,
    stats,
    contractors,
    loading,
    error,
    expiringTickets,
    expiringTicketsLoading,
    filters,
    assignmentLoading,
    assignmentError,
    showDetailModal,
    showCreateModal,
    showEditModal,
    showAssignModal,
    showAuditTrailModal,
    hasFilters,
    loadTickets,
    loadStats,
    loadContractors,
    loadExpiringTickets,
    selectTicket,
    closeDetailModal,
    openCreateModal,
    openEditModal,
    closeModal,
    openAssignModal,
    closeAssignModal,
    openAuditTrailModal,
    closeAuditTrailModal,
    createTicket,
    updateTicket,
    renewTicket,
    closeTicket,
    assignTicket,
    updateFilters,
    clearFilters,
    clearError
  }
})
