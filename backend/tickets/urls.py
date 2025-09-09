from django.urls import path
from .views import (
    TicketListCreateApi,
    TicketDetailApi,
    TicketRenewApi,
    TicketAssignApi,
    TicketCloseApi,
    TicketStatsApi,
    ContractorListApi,
    UserLogsApi,
    TicketLogsApi,
    TicketAuditTrailApi,
    DashboardApi,
)

app_name = 'tickets'

urlpatterns = [
    # Ticket CRUD operations
    path('', TicketListCreateApi.as_view(), name='ticket-list-create'),
    path('<uuid:ticket_id>/', TicketDetailApi.as_view(), name='ticket-detail'),
    
    # Ticket actions
    path('<uuid:ticket_id>/renew/', TicketRenewApi.as_view(), name='ticket-renew'),
    path('<uuid:ticket_id>/assign/', TicketAssignApi.as_view(), name='ticket-assign'),
    path('<uuid:ticket_id>/close/', TicketCloseApi.as_view(), name='ticket-close'),
    
    # Statistics and data
    path('stats/', TicketStatsApi.as_view(), name='ticket-stats'),
    path('contractors/', ContractorListApi.as_view(), name='contractor-list'),
    path('dashboard/', DashboardApi.as_view(), name='dashboard'),
    
    # Logging and audit
    path('logs/users/', UserLogsApi.as_view(), name='user-logs'),
    path('logs/tickets/', TicketLogsApi.as_view(), name='ticket-logs'),
    path('<uuid:ticket_id>/logs/', TicketLogsApi.as_view(), name='ticket-logs-detail'),
    path('<uuid:ticket_id>/audit/', TicketAuditTrailApi.as_view(), name='ticket-audit'),
]
