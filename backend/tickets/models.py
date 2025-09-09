from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
import uuid

User = get_user_model()


class Ticket(models.Model):
    """
    Ticket model for tracking work orders and requests.
    Includes comprehensive user tracking for audit trails.
    """
    
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        help_text="Auto-generated ticket number"
    )
    organization = models.CharField(
        max_length=255,
        help_text="Organization or company name"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        help_text="Current status of the ticket"
    )
    location = models.CharField(
        max_length=255,
        help_text="Location where work is to be performed"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes and details"
    )
    
    # Date fields
    created_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(
        help_text="Date when the ticket expires"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    # User tracking fields
    assigned_contractor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_tickets',
        limit_choices_to={'role': 'contractor'},
        help_text="Contractor assigned to this ticket"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        help_text="User who created this ticket"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='updated_tickets',
        help_text="User who last updated this ticket"
    )
    
    class Meta:
        db_table = "tickets_ticket"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["assigned_contractor"]),
            models.Index(fields=["created_date"]),
            models.Index(fields=["expiration_date"]),
            models.Index(fields=["ticket_number"]),
        ]
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.ticket_number} - {self.organization}"
    
    def save(self, *args, **kwargs):
        """Override save to generate ticket number if not exists."""
        if not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)
    
    def _generate_ticket_number(self):
        """Generate unique ticket number in format TKT-YYYYMMDD-XXXX."""
        today = timezone.now().date()
        date_str = today.strftime('%Y%m%d')
        
        # Get count of tickets created today
        today_count = Ticket.objects.filter(
            created_date__date=today
        ).count()
        
        # Generate sequential number
        sequence = str(today_count + 1).zfill(4)
        
        return f"TKT-{date_str}-{sequence}"
    
    @property
    def is_expired(self):
        """Check if ticket is expired."""
        return timezone.now() > self.expiration_date
    
    @property
    def is_expiring_soon(self):
        """Check if ticket expires within 48 hours."""
        time_diff = self.expiration_date - timezone.now()
        return time_diff.total_seconds() <= 48 * 3600  # 48 hours in seconds
    
    def renew(self, renewed_by, days=15):
        """Extend ticket expiration by specified days (default 15)."""
        from datetime import timedelta
        self.expiration_date += timedelta(days=days)
        self.updated_by = renewed_by
        self.save()


class UserLog(models.Model):
    """
    Log model for tracking user actions across the system.
    Includes ticket-related actions for comprehensive audit trails.
    """
    
    class Action(models.TextChoices):
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PROFILE_UPDATE = "profile_update", "Profile Update"
        PASSWORD_CHANGE = "password_change", "Password Change"
        TWO_FACTOR_ENABLE = "two_factor_enable", "2FA Enable"
        TWO_FACTOR_DISABLE = "two_factor_disable", "2FA Disable"
        TICKET_CREATED = "ticket_created", "Ticket Created"
        TICKET_UPDATED = "ticket_updated", "Ticket Updated"
        TICKET_CLOSED = "ticket_closed", "Ticket Closed"
        TICKET_RENEWED = "ticket_renewed", "Ticket Renewed"
        TICKET_ASSIGNED = "ticket_assigned", "Ticket Assigned"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_logs',
        help_text="User who performed the action"
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        help_text="Type of action performed"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context and details about the action"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which the action was performed"
    )
    related_ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_logs',
        help_text="Related ticket for ticket-specific actions"
    )
    
    class Meta:
        db_table = "tickets_userlog"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["related_ticket"]),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_action_display()} - {self.timestamp}"


class TicketLog(models.Model):
    """
    Log model for tracking all changes and actions on tickets.
    Provides detailed audit trail with before/after values.
    """
    
    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        STATUS_CHANGED = "status_changed", "Status Changed"
        ASSIGNED = "assigned", "Assigned"
        RENEWED = "renewed", "Renewed"
        CLOSED = "closed", "Closed"
        REOPENED = "reopened", "Reopened"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='ticket_logs',
        help_text="Ticket that was modified"
    )
    action_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ticket_actions',
        null=True,
        blank=True,
        help_text="User who performed the action (null for system actions)"
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        help_text="Type of action performed on the ticket"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context about the action"
    )
    previous_values = models.JSONField(
        default=dict,
        blank=True,
        help_text="Previous field values before the change"
    )
    
    class Meta:
        db_table = "tickets_ticketlog"
        indexes = [
            models.Index(fields=["ticket"]),
            models.Index(fields=["action_by"]),
            models.Index(fields=["action"]),
            models.Index(fields=["timestamp"]),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.ticket.ticket_number} - {self.get_action_display()} by {self.action_by.email}"
