import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone

from .services import TicketService, TicketPermissionService, LoggingService, ExpirationService
from .selectors import TicketSelector, LogSelector, DashboardSelector
from .serializers import (
    TicketCreateInputSerializer,
    TicketUpdateInputSerializer,
    TicketRenewInputSerializer,
    TicketAssignInputSerializer,
    TicketCloseInputSerializer,
    TicketFilterInputSerializer,
    LogFilterInputSerializer,
    TicketOutputSerializer,
    TicketListOutputSerializer,
    TicketCreateOutputSerializer,
    TicketUpdateOutputSerializer,
    TicketRenewOutputSerializer,
    TicketAssignOutputSerializer,
    TicketStatsOutputSerializer,
    ContractorOutputSerializer,
    UserLogOutputSerializer,
    TicketLogOutputSerializer,
    AuditTrailOutputSerializer,
    DashboardDataOutputSerializer,
    MessageOutputSerializer,
    ErrorOutputSerializer,
    TicketListResponseSerializer,
    LogListResponseSerializer,
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class TicketPagination(PageNumberPagination):
    """Custom pagination for tickets."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TicketListCreateApi(APIView):
    """
    API for listing and creating tickets with role-based access.
    
    GET /api/tickets/ - List tickets (filtered by user role)
    POST /api/tickets/ - Create ticket (admin only)
    """
    permission_classes = [IsAuthenticated]
    pagination_class = TicketPagination

    def get(self, request):
        """List tickets based on user role with filtering and pagination."""
        try:
            # Parse filter parameters - handle both DRF Request and Django WSGIRequest
            query_params = getattr(request, 'query_params', request.GET)
            filter_serializer = TicketFilterInputSerializer(data=query_params)
            if not filter_serializer.is_valid():
                return Response(
                    ErrorOutputSerializer({"error": "Invalid filter parameters"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            filters = filter_serializer.validated_data
            
            # Get tickets for user
            tickets = TicketSelector.get_tickets_for_user(
                user=request.user,
                status=filters.get('status'),
                search=filters.get('search')
            )
            
            # Apply additional filters
            expiring_soon = filters.get('expiring_soon')
            expired = filters.get('expired')
            
            if expiring_soon and expired:
                # Both filters: use OR logic (tickets that are either expiring soon OR expired)
                from django.db.models import Q
                tickets = tickets.filter(
                    Q(
                        expiration_date__lte=timezone.now() + timezone.timedelta(hours=48),
                        expiration_date__gt=timezone.now(),
                        status__in=['open', 'in_progress']
                    ) | Q(
                        expiration_date__lt=timezone.now(),
                        status__in=['open', 'in_progress']
                    )
                )
            elif expiring_soon:
                # Only expiring soon filter
                tickets = tickets.filter(
                    expiration_date__lte=timezone.now() + timezone.timedelta(hours=48),
                    expiration_date__gt=timezone.now(),
                    status__in=['open', 'in_progress']
                )
            elif expired:
                # Only expired filter
                tickets = tickets.filter(
                    expiration_date__lt=timezone.now(),
                    status__in=['open', 'in_progress']
                )
            
            # Paginate results
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(tickets, request)
            
            if page is not None:
                serializer = TicketListOutputSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = TicketListOutputSerializer(tickets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing tickets for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new ticket (admin only)."""
        try:
            # Validate input
            serializer = TicketCreateInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    ErrorOutputSerializer({"error": "Invalid input data"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            
            # Create ticket using service
            ticket = TicketService.create_ticket(
                created_by=request.user,
                assigned_contractor_id=validated_data['assigned_contractor_id'],
                organization=validated_data['organization'],
                location=validated_data['location'],
                expiration_date=validated_data['expiration_date'],
                notes=validated_data.get('notes', ''),
                ip_address=get_client_ip(request)
            )
            
            logger.info(f"Ticket created: {ticket.ticket_number} by {request.user.email}")
            
            response_data = {
                "message": "Ticket created successfully",
                "ticket": ticket
            }
            response_serializer = TicketCreateOutputSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except PermissionDenied as e:
            logger.warning(f"Permission denied creating ticket for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error creating ticket: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketDetailApi(APIView):
    """
    API for ticket detail operations with role-based access.
    
    GET /api/tickets/{id}/ - Get ticket details
    PUT /api/tickets/{id}/ - Update ticket
    DELETE /api/tickets/{id}/ - Delete ticket (admin only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        """Get ticket details with role-based access control."""
        try:
            ticket = TicketSelector.get_ticket_by_id(ticket_id, request.user)
            if not ticket:
                return Response(
                    ErrorOutputSerializer({"error": "Ticket not found or access denied"}).data,
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = TicketOutputSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, ticket_id):
        """Update ticket with change tracking."""
        try:
            # Validate input
            serializer = TicketUpdateInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    ErrorOutputSerializer({"error": "Invalid input data"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            
            # Update ticket using service
            ticket = TicketService.update_ticket(
                ticket_id=ticket_id,
                updated_by=request.user,
                **validated_data
            )
            
            logger.info(f"Ticket updated: {ticket.ticket_number} by {request.user.email}")
            
            response_data = {
                "message": "Ticket updated successfully",
                "ticket": ticket
            }
            response_serializer = TicketUpdateOutputSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except PermissionDenied as e:
            logger.warning(f"Permission denied updating ticket {ticket_id} for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error updating ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketRenewApi(APIView):
    """
    API for renewing tickets (extending expiration date).
    
    POST /api/tickets/{id}/renew/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        """Renew ticket by extending expiration date."""
        try:
            # Validate input
            serializer = TicketRenewInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    ErrorOutputSerializer({"error": "Invalid input data"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            days = serializer.validated_data.get('days', 15)
            
            # Renew ticket using service
            ticket = TicketService.renew_ticket(
                ticket_id=ticket_id,
                renewed_by=request.user,
                days=days,
                ip_address=get_client_ip(request)
            )
            
            logger.info(f"Ticket renewed: {ticket.ticket_number} by {request.user.email} (+{days} days)")
            
            response_data = {
                "message": f"Ticket renewed successfully for {days} days",
                "ticket": ticket,
                "days_extended": days,
                "new_expiration_date": ticket.expiration_date
            }
            response_serializer = TicketRenewOutputSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except PermissionDenied as e:
            logger.warning(f"Permission denied renewing ticket {ticket_id} for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error renewing ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error renewing ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketAssignApi(APIView):
    """
    API for assigning tickets to contractors (admin only).
    
    POST /api/tickets/{id}/assign/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        """Assign ticket to a contractor."""
        try:
            # Validate input
            serializer = TicketAssignInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    ErrorOutputSerializer({"error": "Invalid input data"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            assigned_contractor_id = serializer.validated_data['assigned_contractor_id']
            
            # Get previous assignee for response
            ticket = TicketSelector.get_ticket_by_id(ticket_id, request.user)
            if not ticket:
                return Response(
                    ErrorOutputSerializer({"error": "Ticket not found or access denied"}).data,
                    status=status.HTTP_404_NOT_FOUND
                )
            
            previous_assignee = ticket.assigned_contractor
            
            # Assign ticket using service
            ticket = TicketService.assign_ticket(
                ticket_id=ticket_id,
                assigned_to_id=assigned_contractor_id,
                assigned_by=request.user,
                ip_address=get_client_ip(request)
            )
            
            logger.info(f"Ticket assigned: {ticket.ticket_number} to {ticket.assigned_contractor.email} by {request.user.email}")
            
            response_data = {
                "message": "Ticket assigned successfully",
                "ticket": ticket,
                "previous_assignee": previous_assignee,
                "new_assignee": ticket.assigned_contractor
            }
            response_serializer = TicketAssignOutputSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except PermissionDenied as e:
            logger.warning(f"Permission denied assigning ticket {ticket_id} for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error assigning ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error assigning ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketCloseApi(APIView):
    """
    API for closing tickets.
    
    POST /api/tickets/{id}/close/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        """Close a ticket."""
        try:
            # Validate input
            serializer = TicketCloseInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    ErrorOutputSerializer({"error": "Invalid input data"}).data,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reason = serializer.validated_data.get('reason')
            
            # Close ticket using service
            ticket = TicketService.close_ticket(
                ticket_id=ticket_id,
                closed_by=request.user,
                reason=reason,
                ip_address=get_client_ip(request)
            )
            
            logger.info(f"Ticket closed: {ticket.ticket_number} by {request.user.email}")
            
            response_data = {
                "message": "Ticket closed successfully",
                "ticket": ticket
            }
            response_serializer = TicketUpdateOutputSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except PermissionDenied as e:
            logger.warning(f"Permission denied closing ticket {ticket_id} for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            logger.warning(f"Validation error closing ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error closing ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketStatsApi(APIView):
    """
    API for ticket statistics based on user role.
    
    GET /api/tickets/stats/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get ticket statistics for the user."""
        try:
            stats = TicketSelector.get_ticket_stats_for_user(request.user)
            serializer = TicketStatsOutputSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving ticket stats for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractorListApi(APIView):
    """
    API for listing contractors (admin only).
    
    GET /api/tickets/contractors/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get list of contractors for ticket assignment."""
        try:
            if not request.user.is_admin:
                return Response(
                    ErrorOutputSerializer({"error": "Permission denied"}).data,
                    status=status.HTTP_403_FORBIDDEN
                )
            
            contractors = TicketSelector.get_contractors_list()
            serializer = ContractorOutputSerializer(contractors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving contractors list: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLogsApi(APIView):
    """
    API for user activity logs with role-based access.
    
    GET /api/tickets/logs/users/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user logs based on role."""
        try:
            query_params = getattr(request, 'query_params', request.GET)
            limit = int(query_params.get('limit', 50))
            logs = LogSelector.get_user_logs_for_user(request.user, limit=limit)
            
            serializer = UserLogOutputSerializer(logs, many=True)
            response_data = {
                "count": len(serializer.data),
                "results": serializer.data
            }
            response_serializer = LogListResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving user logs for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketLogsApi(APIView):
    """
    API for ticket activity logs with role-based access.
    
    GET /api/tickets/logs/tickets/
    GET /api/tickets/{id}/logs/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id=None):
        """Get ticket logs based on role and ticket access."""
        try:
            query_params = getattr(request, 'query_params', request.GET)
            limit = int(query_params.get('limit', 50))
            logs = LogSelector.get_ticket_logs_for_user(
                request.user, 
                ticket_id=ticket_id, 
                limit=limit
            )
            
            serializer = TicketLogOutputSerializer(logs, many=True)
            response_data = {
                "count": len(serializer.data),
                "results": serializer.data
            }
            response_serializer = LogListResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving ticket logs for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TicketAuditTrailApi(APIView):
    """
    API for complete ticket audit trail.
    
    GET /api/tickets/{id}/audit/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_id):
        """Get complete audit trail for a ticket."""
        try:
            audit_trail = LogSelector.get_ticket_audit_trail(ticket_id, request.user)
            
            if not audit_trail:
                return Response(
                    ErrorOutputSerializer({"error": "Ticket not found or access denied"}).data,
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = AuditTrailOutputSerializer(audit_trail, many=True)
            response_data = {
                "count": len(serializer.data),
                "results": serializer.data
            }
            response_serializer = LogListResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving audit trail for ticket {ticket_id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardApi(APIView):
    """
    API for dashboard data with role-based content.
    
    GET /api/tickets/dashboard/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get dashboard data based on user role."""
        try:
            dashboard_data = DashboardSelector.get_dashboard_data_for_user(request.user)
            serializer = DashboardDataOutputSerializer(dashboard_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving dashboard data for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
