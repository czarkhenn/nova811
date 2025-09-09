from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.utils import timezone

from .models import Ticket, UserLog, TicketLog


class TicketLogInline(admin.TabularInline):
    """Inline admin for ticket logs."""
    model = TicketLog
    extra = 0
    readonly_fields = ('timestamp', 'action_by', 'action', 'details', 'previous_values')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class UserLogInline(admin.TabularInline):
    """Inline admin for user logs related to tickets."""
    model = UserLog
    extra = 0
    readonly_fields = ('timestamp', 'user', 'action', 'details', 'ip_address')
    can_delete = False
    fk_name = 'related_ticket'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin interface for tickets with comprehensive audit trails."""
    
    list_display = [
        'ticket_number', 
        'organization', 
        'status_badge', 
        'assigned_contractor_link',
        'created_by_link',
        'expiration_status',
        'created_date',
        'updated_at'
    ]
    
    list_filter = [
        'status',
        'created_date',
        'expiration_date',
        'assigned_contractor__role',
        'created_by__role'
    ]
    
    search_fields = [
        'ticket_number',
        'organization',
        'location',
        'notes',
        'assigned_contractor__email',
        'assigned_contractor__first_name',
        'assigned_contractor__last_name',
        'created_by__email'
    ]
    
    readonly_fields = [
        'id',
        'ticket_number',
        'created_date',
        'updated_at',
        'is_expired',
        'is_expiring_soon',
        'audit_summary'
    ]
    
    fieldsets = (
        ('Ticket Information', {
            'fields': (
                'id',
                'ticket_number',
                'organization',
                'location',
                'status',
                'notes'
            )
        }),
        ('Dates', {
            'fields': (
                'created_date',
                'expiration_date',
                'updated_at',
                'is_expired',
                'is_expiring_soon'
            )
        }),
        ('User Tracking', {
            'fields': (
                'assigned_contractor',
                'created_by',
                'updated_by'
            )
        }),
        ('Audit Information', {
            'fields': ('audit_summary',),
            'classes': ('collapse',)
        })
    )
    
    inlines = [TicketLogInline, UserLogInline]
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'assigned_contractor',
            'created_by',
            'updated_by'
        ).prefetch_related('ticket_logs', 'user_logs')
    
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            'open': '#28a745',
            'in_progress': '#ffc107',
            'closed': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def assigned_contractor_link(self, obj):
        """Display assigned contractor as clickable link."""
        if obj.assigned_contractor:
            url = reverse('admin:users_user_change', args=[obj.assigned_contractor.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                f"{obj.assigned_contractor.first_name} {obj.assigned_contractor.last_name}"
            )
        return '-'
    assigned_contractor_link.short_description = 'Assigned Contractor'
    
    def created_by_link(self, obj):
        """Display creator as clickable link."""
        if obj.created_by:
            url = reverse('admin:users_user_change', args=[obj.created_by.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                f"{obj.created_by.first_name} {obj.created_by.last_name}"
            )
        return '-'
    created_by_link.short_description = 'Created By'
    
    def expiration_status(self, obj):
        """Display expiration status with color coding."""
        if obj.is_expired:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">EXPIRED</span>'
            )
        elif obj.is_expiring_soon:
            return format_html(
                '<span style="color: #fd7e14; font-weight: bold;">EXPIRING SOON</span>'
            )
        else:
            days_left = (obj.expiration_date - timezone.now()).days
            return format_html(
                '<span style="color: #28a745;">{} days left</span>',
                days_left
            )
    expiration_status.short_description = 'Expiration Status'
    
    def audit_summary(self, obj):
        """Display audit trail summary."""
        if not obj.pk:
            return "Save the ticket to view audit trail"
        
        ticket_logs_count = obj.ticket_logs.count()
        user_logs_count = obj.user_logs.count()
        
        html = f"""
        <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
            <h4>Audit Summary</h4>
            <p><strong>Ticket Actions:</strong> {ticket_logs_count}</p>
            <p><strong>User Actions:</strong> {user_logs_count}</p>
            
            <h5>Recent Activity:</h5>
            <ul>
        """
        
        # Get recent logs
        recent_logs = obj.ticket_logs.select_related('action_by').order_by('-timestamp')[:5]
        for log in recent_logs:
            user_name = log.action_by.get_full_name() if log.action_by else "System"
            html += f"<li>{log.timestamp.strftime('%Y-%m-%d %H:%M')} - {user_name}: {log.get_action_display()}</li>"
        
        html += "</ul></div>"
        return mark_safe(html)
    audit_summary.short_description = 'Audit Trail'


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    """Admin interface for user logs."""
    
    list_display = [
        'timestamp',
        'user_link',
        'action_display',
        'related_ticket_link',
        'ip_address'
    ]
    
    list_filter = [
        'action',
        'timestamp',
        'user__role'
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'related_ticket__ticket_number',
        'ip_address'
    ]
    
    readonly_fields = [
        'id',
        'user',
        'action',
        'timestamp',
        'details',
        'ip_address',
        'related_ticket'
    ]
    
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'user',
            'related_ticket'
        )
    
    def user_link(self, obj):
        """Display user as clickable link."""
        url = reverse('admin:users_user_change', args=[obj.user.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.user.get_full_name() or obj.user.email
        )
    user_link.short_description = 'User'
    
    def action_display(self, obj):
        """Display action with color coding."""
        colors = {
            'login': '#28a745',
            'logout': '#6c757d',
            'ticket_created': '#007bff',
            'ticket_updated': '#ffc107',
            'ticket_closed': '#dc3545',
            'ticket_renewed': '#17a2b8'
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_display.short_description = 'Action'
    
    def related_ticket_link(self, obj):
        """Display related ticket as clickable link."""
        if obj.related_ticket:
            url = reverse('admin:tickets_ticket_change', args=[obj.related_ticket.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.related_ticket.ticket_number
            )
        return '-'
    related_ticket_link.short_description = 'Related Ticket'
    
    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make logs read-only."""
        return False


@admin.register(TicketLog)
class TicketLogAdmin(admin.ModelAdmin):
    """Admin interface for ticket logs."""
    
    list_display = [
        'timestamp',
        'ticket_link',
        'action_by_link',
        'action_display',
        'details_summary'
    ]
    
    list_filter = [
        'action',
        'timestamp',
        'action_by__role'
    ]
    
    search_fields = [
        'ticket__ticket_number',
        'ticket__organization',
        'action_by__email',
        'action_by__first_name',
        'action_by__last_name'
    ]
    
    readonly_fields = [
        'id',
        'ticket',
        'action_by',
        'action',
        'timestamp',
        'details',
        'previous_values'
    ]
    
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        """Optimize queryset with related objects."""
        return super().get_queryset(request).select_related(
            'ticket',
            'action_by'
        )
    
    def ticket_link(self, obj):
        """Display ticket as clickable link."""
        url = reverse('admin:tickets_ticket_change', args=[obj.ticket.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.ticket.ticket_number
        )
    ticket_link.short_description = 'Ticket'
    
    def action_by_link(self, obj):
        """Display action performer as clickable link."""
        if obj.action_by:
            url = reverse('admin:users_user_change', args=[obj.action_by.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.action_by.get_full_name() or obj.action_by.email
            )
        return 'System'
    action_by_link.short_description = 'Action By'
    
    def action_display(self, obj):
        """Display action with color coding."""
        colors = {
            'created': '#28a745',
            'updated': '#ffc107',
            'status_changed': '#007bff',
            'assigned': '#17a2b8',
            'renewed': '#20c997',
            'closed': '#dc3545'
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_display.short_description = 'Action'
    
    def details_summary(self, obj):
        """Display summary of details."""
        if obj.details:
            # Show first few keys from details
            keys = list(obj.details.keys())[:3]
            if len(keys) > 0:
                summary = ', '.join(keys)
                if len(obj.details) > 3:
                    summary += '...'
                return summary
        return '-'
    details_summary.short_description = 'Details'
    
    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make logs read-only."""
        return False


# Admin site customization
admin.site.site_header = "Nova811 Ticket Management"
admin.site.site_title = "Nova811 Admin"
admin.site.index_title = "Welcome to Nova811 Administration"
