from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from .models import Ticket, UserLog, TicketLog

User = get_user_model()
logger = logging.getLogger(__name__)


class TicketPermissionService:
    """
    Service for handling ticket permissions and authorization.
    """
    
    @staticmethod
    def can_view_ticket(user, ticket):
        """
        Check if user can view a specific ticket.
        Admins can view all tickets, contractors only their assigned tickets.
        """
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user.is_contractor:
            return ticket.assigned_contractor == user
        
        return False
    
    @staticmethod
    def can_create_ticket(user):
        """
        Check if user can create tickets.
        Only admins can create tickets.
        """
        return user.is_authenticated and user.is_admin
    
    @staticmethod
    def can_update_ticket(user, ticket):
        """
        Check if user can update a specific ticket.
        Admins can update all tickets, contractors can update their assigned tickets.
        """
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user.is_contractor:
            return ticket.assigned_contractor == user and ticket.status != Ticket.Status.CLOSED
        
        return False
    
    @staticmethod
    def can_assign_ticket(user):
        """
        Check if user can assign tickets.
        Only admins can assign tickets.
        """
        return user.is_authenticated and user.is_admin
    
    @staticmethod
    def can_renew_ticket(user, ticket):
        """
        Check if user can renew a specific ticket.
        Admins and assigned contractors can renew tickets.
        """
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user.is_contractor:
            return ticket.assigned_contractor == user
        
        return False


class LoggingService:
    """
    Service for logging user actions and ticket changes.
    """
    
    @staticmethod
    def log_user_action(user, action, details=None, related_ticket=None, ip_address=None):
        """
        Log a user action with optional ticket relation.
        """
        try:
            UserLog.objects.create(
                user=user,
                action=action,
                details=details or {},
                related_ticket=related_ticket,
                ip_address=ip_address
            )
            logger.info(f"User action logged: {user.email} - {action}")
        except Exception as e:
            logger.error(f"Failed to log user action: {str(e)}")
    
    @staticmethod
    def log_ticket_action(ticket, action_by, action, details=None, previous_values=None):
        """
        Log a ticket action with before/after values.
        """
        try:
            TicketLog.objects.create(
                ticket=ticket,
                action_by=action_by,
                action=action,
                details=details or {},
                previous_values=previous_values or {}
            )
            logger.info(f"Ticket action logged: {ticket.ticket_number} - {action} by {action_by.email}")
        except Exception as e:
            logger.error(f"Failed to log ticket action: {str(e)}")


class TicketService:
    """
    Service for ticket management operations with comprehensive logging.
    """
    
    @staticmethod
    @transaction.atomic
    def create_ticket(created_by, assigned_contractor_id, organization, location, 
                     expiration_date, notes="", ip_address=None):
        """
        Create a new ticket with full audit logging.
        """
        # Check permissions
        if not TicketPermissionService.can_create_ticket(created_by):
            raise PermissionDenied("You don't have permission to create tickets")
        
        # Validate assigned contractor
        try:
            assigned_contractor = User.objects.get(
                id=assigned_contractor_id, 
                role=User.Role.CONTRACTOR
            )
        except User.DoesNotExist:
            raise ValidationError("Invalid contractor assignment")
        
        # Validate expiration date
        if expiration_date <= timezone.now():
            raise ValidationError("Expiration date must be in the future")
        
        # Create ticket
        ticket = Ticket.objects.create(
            organization=organization,
            location=location,
            expiration_date=expiration_date,
            notes=notes,
            assigned_contractor=assigned_contractor,
            created_by=created_by,
            updated_by=created_by
        )
        
        # Log actions
        LoggingService.log_user_action(
            user=created_by,
            action=UserLog.Action.TICKET_CREATED,
            details={
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "organization": organization,
                "assigned_to": assigned_contractor.email
            },
            related_ticket=ticket,
            ip_address=ip_address
        )
        
        LoggingService.log_ticket_action(
            ticket=ticket,
            action_by=created_by,
            action=TicketLog.Action.CREATED,
            details={
                "organization": organization,
                "location": location,
                "assigned_contractor": assigned_contractor.email,
                "expiration_date": expiration_date.isoformat()
            }
        )
        
        logger.info(f"Ticket created: {ticket.ticket_number} by {created_by.email}")
        return ticket
    
    @staticmethod
    @transaction.atomic
    def update_ticket(ticket_id, updated_by, **update_data):
        """
        Update a ticket with change tracking and logging.
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError("Ticket not found")
        
        # Check permissions
        if not TicketPermissionService.can_update_ticket(updated_by, ticket):
            raise PermissionDenied("You don't have permission to update this ticket")
        
        # Store previous values for audit trail
        previous_values = {
            "organization": ticket.organization,
            "status": ticket.status,
            "location": ticket.location,
            "notes": ticket.notes,
            "expiration_date": ticket.expiration_date.isoformat()
        }
        
        # Track what changed
        changes = {}
        
        # Update allowed fields
        if 'organization' in update_data:
            if ticket.organization != update_data['organization']:
                changes['organization'] = {
                    'old': ticket.organization,
                    'new': update_data['organization']
                }
            ticket.organization = update_data['organization']
        
        if 'status' in update_data:
            if ticket.status != update_data['status']:
                changes['status'] = {
                    'old': ticket.status,
                    'new': update_data['status']
                }
            ticket.status = update_data['status']
        
        if 'location' in update_data:
            if ticket.location != update_data['location']:
                changes['location'] = {
                    'old': ticket.location,
                    'new': update_data['location']
                }
            ticket.location = update_data['location']
        
        if 'notes' in update_data:
            if ticket.notes != update_data['notes']:
                changes['notes'] = {
                    'old': ticket.notes,
                    'new': update_data['notes']
                }
            ticket.notes = update_data['notes']
        
        if 'expiration_date' in update_data:
            new_expiration = update_data['expiration_date']
            if ticket.expiration_date != new_expiration:
                changes['expiration_date'] = {
                    'old': ticket.expiration_date.isoformat(),
                    'new': new_expiration.isoformat()
                }
            ticket.expiration_date = new_expiration
        
        # Update tracking fields
        ticket.updated_by = updated_by
        ticket.save()
        
        # Log actions if there were changes
        if changes:
            LoggingService.log_user_action(
                user=updated_by,
                action=UserLog.Action.TICKET_UPDATED,
                details={
                    "ticket_id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "changes": changes
                },
                related_ticket=ticket
            )
            
            LoggingService.log_ticket_action(
                ticket=ticket,
                action_by=updated_by,
                action=TicketLog.Action.UPDATED,
                details={"changes": changes},
                previous_values=previous_values
            )
            
            logger.info(f"Ticket updated: {ticket.ticket_number} by {updated_by.email}")
        
        return ticket
    
    @staticmethod
    @transaction.atomic
    def close_ticket(ticket_id, closed_by, reason=None, ip_address=None):
        """
        Close a ticket with logging.
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError("Ticket not found")
        
        # Check permissions
        if not TicketPermissionService.can_update_ticket(closed_by, ticket):
            raise PermissionDenied("You don't have permission to close this ticket")
        
        if ticket.status == Ticket.Status.CLOSED:
            raise ValidationError("Ticket is already closed")
        
        # Store previous status
        previous_status = ticket.status
        
        # Close ticket
        ticket.status = Ticket.Status.CLOSED
        ticket.updated_by = closed_by
        ticket.save()
        
        # Log actions
        LoggingService.log_user_action(
            user=closed_by,
            action=UserLog.Action.TICKET_CLOSED,
            details={
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "reason": reason,
                "previous_status": previous_status
            },
            related_ticket=ticket,
            ip_address=ip_address
        )
        
        LoggingService.log_ticket_action(
            ticket=ticket,
            action_by=closed_by,
            action=TicketLog.Action.CLOSED,
            details={"reason": reason},
            previous_values={"status": previous_status}
        )
        
        logger.info(f"Ticket closed: {ticket.ticket_number} by {closed_by.email}")
        return ticket
    
    @staticmethod
    @transaction.atomic
    def renew_ticket(ticket_id, renewed_by, days=15, ip_address=None):
        """
        Renew a ticket by extending expiration date.
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError("Ticket not found")
        
        # Check permissions
        if not TicketPermissionService.can_renew_ticket(renewed_by, ticket):
            raise PermissionDenied("You don't have permission to renew this ticket")
        
        # Store previous expiration date
        previous_expiration = ticket.expiration_date
        
        # Renew ticket
        ticket.renew(renewed_by, days)
        
        # Log actions
        LoggingService.log_user_action(
            user=renewed_by,
            action=UserLog.Action.TICKET_RENEWED,
            details={
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "days_extended": days,
                "previous_expiration": previous_expiration.isoformat(),
                "new_expiration": ticket.expiration_date.isoformat()
            },
            related_ticket=ticket,
            ip_address=ip_address
        )
        
        LoggingService.log_ticket_action(
            ticket=ticket,
            action_by=renewed_by,
            action=TicketLog.Action.RENEWED,
            details={
                "days_extended": days,
                "new_expiration": ticket.expiration_date.isoformat()
            },
            previous_values={"expiration_date": previous_expiration.isoformat()}
        )
        
        logger.info(f"Ticket renewed: {ticket.ticket_number} by {renewed_by.email} (+{days} days)")
        return ticket
    
    @staticmethod
    @transaction.atomic
    def assign_ticket(ticket_id, assigned_to_id, assigned_by, ip_address=None):
        """
        Assign a ticket to a contractor.
        """
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError("Ticket not found")
        
        # Check permissions
        if not TicketPermissionService.can_assign_ticket(assigned_by):
            raise PermissionDenied("You don't have permission to assign tickets")
        
        # Validate new assignee
        try:
            new_assignee = User.objects.get(
                id=assigned_to_id,
                role=User.Role.CONTRACTOR
            )
        except User.DoesNotExist:
            raise ValidationError("Invalid contractor for assignment")
        
        # Store previous assignee
        previous_assignee = ticket.assigned_contractor
        
        if previous_assignee == new_assignee:
            raise ValidationError("Ticket is already assigned to this contractor")
        
        # Assign ticket
        ticket.assigned_contractor = new_assignee
        ticket.updated_by = assigned_by
        ticket.save()
        
        # Log actions
        LoggingService.log_user_action(
            user=assigned_by,
            action=UserLog.Action.TICKET_ASSIGNED,
            details={
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "previous_assignee": previous_assignee.email,
                "new_assignee": new_assignee.email
            },
            related_ticket=ticket,
            ip_address=ip_address
        )
        
        LoggingService.log_ticket_action(
            ticket=ticket,
            action_by=assigned_by,
            action=TicketLog.Action.ASSIGNED,
            details={"new_assignee": new_assignee.email},
            previous_values={"assigned_contractor": previous_assignee.email}
        )
        
        logger.info(f"Ticket assigned: {ticket.ticket_number} to {new_assignee.email} by {assigned_by.email}")
        return ticket


class ExpirationService:
    """
    Service for handling ticket expiration checks and alerts.
    """
    
    @staticmethod
    def get_expiring_tickets(hours=48):
        """
        Get tickets that will expire within specified hours.
        """
        cutoff_time = timezone.now() + timedelta(hours=hours)
        return Ticket.objects.filter(
            expiration_date__lte=cutoff_time,
            expiration_date__gt=timezone.now(),
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        ).select_related('assigned_contractor', 'created_by')
    
    @staticmethod
    def get_expired_tickets():
        """
        Get tickets that have already expired.
        """
        return Ticket.objects.filter(
            expiration_date__lt=timezone.now(),
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        ).select_related('assigned_contractor', 'created_by')
    
    @staticmethod
    def send_expiration_alerts():
        """
        Send alerts for tickets expiring within 48 hours.
        Currently logs to console, can be extended for email/database alerts.
        """
        expiring_tickets = ExpirationService.get_expiring_tickets()
        
        for ticket in expiring_tickets:
            time_until_expiry = ticket.expiration_date - timezone.now()
            hours_remaining = int(time_until_expiry.total_seconds() / 3600)
            
            alert_message = (
                f"TICKET EXPIRATION ALERT: {ticket.ticket_number} "
                f"({ticket.organization}) expires in {hours_remaining} hours. "
                f"Assigned to: {ticket.assigned_contractor.email}"
            )
            
            logger.warning(alert_message)
            print(f"[ALERT] {alert_message}")
        
        return len(expiring_tickets)
    
    @staticmethod
    @transaction.atomic
    def mark_expired_tickets():
        """
        Automatically mark expired tickets and log the action.
        """
        expired_tickets = ExpirationService.get_expired_tickets()
        updated_count = 0
        
        for ticket in expired_tickets:
            # Store previous status
            previous_status = ticket.status
            
            # Mark as closed
            ticket.status = Ticket.Status.CLOSED
            ticket.save()
            
            # Log the automatic closure
            LoggingService.log_ticket_action(
                ticket=ticket,
                action_by=None,  # System action
                action=TicketLog.Action.CLOSED,
                details={"reason": "Automatically closed due to expiration"},
                previous_values={"status": previous_status}
            )
            
            logger.info(f"Ticket automatically expired: {ticket.ticket_number}")
            updated_count += 1
        
        return updated_count
