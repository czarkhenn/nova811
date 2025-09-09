from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import timedelta

from .models import Ticket, UserLog, TicketLog

User = get_user_model()


class TicketSelector:
    """
    Selector for ticket-related queries with role-based access control.
    """
    
    @staticmethod
    def get_tickets_for_user(user, status=None, search=None):
        """
        Get tickets based on user role with optional filtering.
        Admins see all tickets, contractors see tickets they created or are assigned to.
        """
        # Base queryset with optimized joins
        queryset = Ticket.objects.select_related(
            'assigned_contractor',
            'created_by',
            'updated_by'
        )
        
        # Apply role-based filtering
        if user.is_admin:
            # Admins can see all tickets
            pass
        elif user.is_contractor:
            # Contractors can see tickets they created or are assigned to
            queryset = queryset.filter(
                Q(created_by=user) |
                Q(assigned_contractor=user)
            )
        else:
            # No access for other roles
            return queryset.none()
        
        # Apply status filter
        if status:
            queryset = queryset.filter(status=status)
        
        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(ticket_number__icontains=search) |
                Q(organization__icontains=search) |
                Q(location__icontains=search) |
                Q(notes__icontains=search)
            )
        
        return queryset.order_by('-created_date')
    
    @staticmethod
    def get_ticket_by_id(ticket_id, user):
        """
        Get a specific ticket by ID with role-based access control.
        """
        try:
            ticket = Ticket.objects.select_related(
                'assigned_contractor',
                'created_by',
                'updated_by'
            ).prefetch_related(
                Prefetch(
                    'ticket_logs',
                    queryset=TicketLog.objects.select_related('action_by').order_by('-timestamp')
                )
            ).get(id=ticket_id)
            
            # Check access permissions
            if user.is_admin:
                return ticket
            elif user.is_contractor and (ticket.assigned_contractor == user or ticket.created_by == user):
                return ticket
            else:
                return None
                
        except Ticket.DoesNotExist:
            return None
    
    @staticmethod
    def get_ticket_stats_for_user(user):
        """
        Get ticket statistics based on user role.
        """
        # Base queryset based on user role
        if user.is_admin:
            base_queryset = Ticket.objects.all()
        elif user.is_contractor:
            base_queryset = Ticket.objects.filter(
                Q(created_by=user) |
                Q(assigned_contractor=user)
            )
        else:
            return {}
        
        # Calculate statistics
        stats = {
            'total': base_queryset.count(),
            'open': base_queryset.filter(status=Ticket.Status.OPEN).count(),
            'in_progress': base_queryset.filter(status=Ticket.Status.IN_PROGRESS).count(),
            'closed': base_queryset.filter(status=Ticket.Status.CLOSED).count(),
            'expiring_soon': base_queryset.filter(
                expiration_date__lte=timezone.now() + timedelta(hours=48),
                expiration_date__gt=timezone.now(),
                status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
            ).count(),
            'expired': base_queryset.filter(
                expiration_date__lt=timezone.now(),
                status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
            ).count()
        }
        
        return stats
    
    @staticmethod
    def get_expiring_tickets_for_user(user, hours=48):
        """
        Get tickets expiring within specified hours for a user.
        """
        cutoff_time = timezone.now() + timedelta(hours=hours)
        
        # Base queryset based on user role
        if user.is_admin:
            queryset = Ticket.objects.all()
        elif user.is_contractor:
            queryset = Ticket.objects.filter(
                Q(created_by=user) |
                Q(assigned_contractor=user)
            )
        else:
            return Ticket.objects.none()
        
        return queryset.filter(
            expiration_date__lte=cutoff_time,
            expiration_date__gt=timezone.now(),
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        ).select_related('assigned_contractor', 'created_by').order_by('expiration_date')
    
    @staticmethod
    def get_recent_tickets_for_user(user, limit=10):
        """
        Get recently created tickets for a user.
        """
        # Base queryset based on user role
        if user.is_admin:
            queryset = Ticket.objects.all()
        elif user.is_contractor:
            queryset = Ticket.objects.filter(
                Q(created_by=user) |
                Q(assigned_contractor=user)
            )
        else:
            return Ticket.objects.none()
        
        return queryset.select_related(
            'assigned_contractor',
            'created_by'
        ).order_by('-created_date')[:limit]
    
    @staticmethod
    def get_contractors_list():
        """
        Get list of contractors for ticket assignment.
        Only used by admins.
        """
        return User.objects.filter(
            role=User.Role.CONTRACTOR,
            is_active=True
        ).order_by('first_name', 'last_name')


class LogSelector:
    """
    Selector for log-related queries with role-based access control.
    """
    
    @staticmethod
    def get_user_logs_for_user(user, limit=50):
        """
        Get user logs based on role.
        Admins can see all logs, contractors see logs related to tickets they created or are assigned to.
        """
        if user.is_admin:
            # Admins can see all user logs
            queryset = UserLog.objects.select_related(
                'user',
                'related_ticket'
            ).order_by('-timestamp')[:limit]
        elif user.is_contractor:
            # Contractors can see logs related to tickets they created or are assigned to
            queryset = UserLog.objects.filter(
                Q(related_ticket__created_by=user) |
                Q(related_ticket__assigned_contractor=user) |
                Q(user=user)  # Also include their own logs
            ).select_related(
                'user',
                'related_ticket'
            ).order_by('-timestamp')[:limit]
        else:
            return UserLog.objects.none()
        
        return queryset
    
    @staticmethod
    def get_ticket_logs_for_user(user, ticket_id=None, limit=50):
        """
        Get ticket logs based on user role and ticket access.
        """
        # Base queryset
        queryset = TicketLog.objects.select_related(
            'ticket',
            'action_by'
        )
        
        # Filter by specific ticket if provided
        if ticket_id:
            queryset = queryset.filter(ticket_id=ticket_id)
        
        # Apply role-based filtering
        if user.is_admin:
            # Admins can see all ticket logs
            pass
        elif user.is_contractor:
            # Contractors can see logs for tickets they created or are assigned to
            queryset = queryset.filter(
                Q(ticket__created_by=user) |
                Q(ticket__assigned_contractor=user)
            )
        else:
            return queryset.none()
        
        return queryset.order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_recent_activity_for_user(user, limit=20):
        """
        Get recent activity combining user logs and ticket logs.
        """
        activities = []
        
        # Get recent user logs
        user_logs = LogSelector.get_user_logs_for_user(user, limit=limit//2)
        for log in user_logs:
            activities.append({
                'type': 'user_log',
                'timestamp': log.timestamp,
                'user': log.user,
                'action': log.get_action_display(),
                'details': log.details,
                'related_ticket': log.related_ticket
            })
        
        # Get recent ticket logs
        ticket_logs = LogSelector.get_ticket_logs_for_user(user, limit=limit//2)
        for log in ticket_logs:
            activities.append({
                'type': 'ticket_log',
                'timestamp': log.timestamp,
                'user': log.action_by,
                'action': log.get_action_display(),
                'details': log.details,
                'ticket': log.ticket
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    @staticmethod
    def get_ticket_audit_trail(ticket_id, user):
        """
        Get complete audit trail for a specific ticket.
        """
        # First check if user can access this ticket
        ticket = TicketSelector.get_ticket_by_id(ticket_id, user)
        if not ticket:
            return []
        
        # Get all logs for this ticket
        ticket_logs = TicketLog.objects.filter(
            ticket_id=ticket_id
        ).select_related('action_by').order_by('-timestamp')
        
        user_logs = UserLog.objects.filter(
            related_ticket_id=ticket_id
        ).select_related('user').order_by('-timestamp')
        
        # Combine and sort
        audit_trail = []
        
        for log in ticket_logs:
            audit_trail.append({
                'type': 'ticket_action',
                'timestamp': log.timestamp,
                'user': log.action_by,
                'action': log.get_action_display(),
                'details': log.details,
                'previous_values': log.previous_values
            })
        
        for log in user_logs:
            audit_trail.append({
                'type': 'user_action',
                'timestamp': log.timestamp,
                'user': log.user,
                'action': log.get_action_display(),
                'details': log.details,
                'ip_address': log.ip_address
            })
        
        # Sort by timestamp
        audit_trail.sort(key=lambda x: x['timestamp'], reverse=True)
        return audit_trail


class DashboardSelector:
    """
    Selector for dashboard-related queries.
    """
    
    @staticmethod
    def get_dashboard_data_for_user(user):
        """
        Get comprehensive dashboard data based on user role.
        """
        data = {
            'ticket_stats': TicketSelector.get_ticket_stats_for_user(user),
            'recent_tickets': TicketSelector.get_recent_tickets_for_user(user, limit=5),
            'expiring_tickets': TicketSelector.get_expiring_tickets_for_user(user),
            'recent_activity': LogSelector.get_recent_activity_for_user(user, limit=10)
        }
        
        # Add admin-specific data
        if user.is_admin:
            data['all_contractors'] = TicketSelector.get_contractors_list()
            data['system_stats'] = {
                'total_users': User.objects.count(),
                'active_contractors': User.objects.filter(
                    role=User.Role.CONTRACTOR,
                    is_active=True
                ).count(),
                'total_tickets_today': Ticket.objects.filter(
                    created_date__date=timezone.now().date()
                ).count()
            }
        
        return data
    
    @staticmethod
    def get_ticket_summary_by_status():
        """
        Get ticket count summary by status (admin only).
        """
        return Ticket.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
    
    @staticmethod
    def get_ticket_summary_by_contractor():
        """
        Get ticket count summary by contractor (admin only).
        """
        return Ticket.objects.values(
            'assigned_contractor__first_name',
            'assigned_contractor__last_name',
            'assigned_contractor__email'
        ).annotate(
            total_tickets=Count('id'),
            open_tickets=Count('id', filter=Q(status=Ticket.Status.OPEN)),
            in_progress_tickets=Count('id', filter=Q(status=Ticket.Status.IN_PROGRESS)),
            closed_tickets=Count('id', filter=Q(status=Ticket.Status.CLOSED))
        ).order_by('assigned_contractor__first_name')
