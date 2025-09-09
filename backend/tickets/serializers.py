from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime

from .models import Ticket, UserLog, TicketLog

User = get_user_model()


# Input Serializers
class TicketCreateInputSerializer(serializers.Serializer):
    """Input serializer for creating tickets."""
    
    organization = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)
    expiration_date = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True)
    assigned_contractor_id = serializers.UUIDField()
    
    def validate_expiration_date(self, value):
        """Validate that expiration date is in the future."""
        if value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value
    
    def validate_assigned_contractor_id(self, value):
        """Validate that the contractor exists and has the correct role."""
        try:
            contractor = User.objects.get(id=value, role=User.Role.CONTRACTOR)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid contractor ID")


class TicketUpdateInputSerializer(serializers.Serializer):
    """Input serializer for updating tickets."""
    
    organization = serializers.CharField(max_length=255, required=False)
    location = serializers.CharField(max_length=255, required=False)
    status = serializers.ChoiceField(choices=Ticket.Status.choices, required=False)
    expiration_date = serializers.DateTimeField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_expiration_date(self, value):
        """Validate that expiration date is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value


class TicketRenewInputSerializer(serializers.Serializer):
    """Input serializer for renewing tickets."""
    
    days = serializers.IntegerField(default=15, min_value=1, max_value=365)


class TicketAssignInputSerializer(serializers.Serializer):
    """Input serializer for assigning tickets."""
    
    assigned_contractor_id = serializers.UUIDField()
    
    def validate_assigned_contractor_id(self, value):
        """Validate that the contractor exists and has the correct role."""
        try:
            contractor = User.objects.get(id=value, role=User.Role.CONTRACTOR)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid contractor ID")


class TicketCloseInputSerializer(serializers.Serializer):
    """Input serializer for closing tickets."""
    
    reason = serializers.CharField(required=False, allow_blank=True)


# Output Serializers
class UserBasicOutputSerializer(serializers.ModelSerializer):
    """Basic user information for ticket-related responses."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']


class TicketLogOutputSerializer(serializers.ModelSerializer):
    """Output serializer for ticket logs."""
    
    action_by = UserBasicOutputSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = TicketLog
        fields = [
            'id', 'action', 'action_display', 'timestamp', 
            'details', 'previous_values', 'action_by'
        ]


class UserLogOutputSerializer(serializers.ModelSerializer):
    """Output serializer for user logs."""
    
    user = UserBasicOutputSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    related_ticket_number = serializers.CharField(source='related_ticket.ticket_number', read_only=True)
    
    class Meta:
        model = UserLog
        fields = [
            'id', 'action', 'action_display', 'timestamp', 
            'details', 'ip_address', 'user', 'related_ticket_number'
        ]


class TicketOutputSerializer(serializers.ModelSerializer):
    """Output serializer for tickets with full user information."""
    
    assigned_contractor = UserBasicOutputSerializer(read_only=True)
    created_by = UserBasicOutputSerializer(read_only=True)
    updated_by = UserBasicOutputSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    ticket_logs = TicketLogOutputSerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'organization', 'location', 'status', 
            'status_display', 'notes', 'created_date', 'expiration_date', 
            'updated_at', 'is_expired', 'is_expiring_soon',
            'assigned_contractor', 'created_by', 'updated_by', 'ticket_logs'
        ]


class TicketListOutputSerializer(serializers.ModelSerializer):
    """Simplified output serializer for ticket lists."""
    
    assigned_contractor = UserBasicOutputSerializer(read_only=True)
    created_by = UserBasicOutputSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'organization', 'location', 'status', 
            'status_display', 'created_date', 'expiration_date', 
            'is_expired', 'is_expiring_soon', 'assigned_contractor', 'created_by'
        ]


class TicketStatsOutputSerializer(serializers.Serializer):
    """Output serializer for ticket statistics."""
    
    total = serializers.IntegerField()
    open = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    closed = serializers.IntegerField()
    expiring_soon = serializers.IntegerField()
    expired = serializers.IntegerField()


class ContractorOutputSerializer(serializers.ModelSerializer):
    """Output serializer for contractor list."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class ActivityOutputSerializer(serializers.Serializer):
    """Output serializer for activity feed."""
    
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    user = UserBasicOutputSerializer()
    action = serializers.CharField()
    details = serializers.JSONField()
    related_ticket = serializers.CharField(required=False)
    ticket = serializers.CharField(required=False)


class AuditTrailOutputSerializer(serializers.Serializer):
    """Output serializer for audit trail."""
    
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    user = UserBasicOutputSerializer(allow_null=True)
    action = serializers.CharField()
    details = serializers.JSONField()
    previous_values = serializers.JSONField(required=False)
    ip_address = serializers.IPAddressField(required=False)


class DashboardDataOutputSerializer(serializers.Serializer):
    """Output serializer for dashboard data."""
    
    ticket_stats = TicketStatsOutputSerializer()
    recent_tickets = TicketListOutputSerializer(many=True)
    expiring_tickets = TicketListOutputSerializer(many=True)
    recent_activity = ActivityOutputSerializer(many=True)
    all_contractors = ContractorOutputSerializer(many=True, required=False)
    system_stats = serializers.JSONField(required=False)


# Response Serializers
class MessageOutputSerializer(serializers.Serializer):
    """Generic message response serializer."""
    
    message = serializers.CharField()


class ErrorOutputSerializer(serializers.Serializer):
    """Generic error response serializer."""
    
    error = serializers.CharField()


class TicketCreateOutputSerializer(serializers.Serializer):
    """Response serializer for ticket creation."""
    
    message = serializers.CharField()
    ticket = TicketOutputSerializer()


class TicketUpdateOutputSerializer(serializers.Serializer):
    """Response serializer for ticket updates."""
    
    message = serializers.CharField()
    ticket = TicketOutputSerializer()


class TicketRenewOutputSerializer(serializers.Serializer):
    """Response serializer for ticket renewal."""
    
    message = serializers.CharField()
    ticket = TicketOutputSerializer()
    days_extended = serializers.IntegerField()
    new_expiration_date = serializers.DateTimeField()


class TicketAssignOutputSerializer(serializers.Serializer):
    """Response serializer for ticket assignment."""
    
    message = serializers.CharField()
    ticket = TicketOutputSerializer()
    previous_assignee = UserBasicOutputSerializer()
    new_assignee = UserBasicOutputSerializer()


class TicketListResponseSerializer(serializers.Serializer):
    """Response serializer for ticket list with pagination info."""
    
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = TicketListOutputSerializer(many=True)


class LogListResponseSerializer(serializers.Serializer):
    """Response serializer for log lists."""
    
    count = serializers.IntegerField()
    results = serializers.ListField()


# Filter Serializers
class TicketFilterInputSerializer(serializers.Serializer):
    """Input serializer for ticket filtering."""
    
    status = serializers.ChoiceField(choices=Ticket.Status.choices, required=False)
    search = serializers.CharField(required=False, allow_blank=True)
    assigned_contractor = serializers.UUIDField(required=False)
    created_by = serializers.UUIDField(required=False)
    expiring_soon = serializers.BooleanField(required=False)
    expired = serializers.BooleanField(required=False)
    
    def validate_assigned_contractor(self, value):
        """Validate contractor exists."""
        if value:
            try:
                User.objects.get(id=value, role=User.Role.CONTRACTOR)
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid contractor ID")
        return value
    
    def validate_created_by(self, value):
        """Validate creator exists."""
        if value:
            try:
                User.objects.get(id=value)
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid user ID")
        return value


class LogFilterInputSerializer(serializers.Serializer):
    """Input serializer for log filtering."""
    
    action = serializers.CharField(required=False)
    user = serializers.UUIDField(required=False)
    ticket = serializers.UUIDField(required=False)
    start_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)
    
    def validate_user(self, value):
        """Validate user exists."""
        if value:
            try:
                User.objects.get(id=value)
                return value
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid user ID")
        return value
    
    def validate_ticket(self, value):
        """Validate ticket exists."""
        if value:
            try:
                Ticket.objects.get(id=value)
                return value
            except Ticket.DoesNotExist:
                raise serializers.ValidationError("Invalid ticket ID")
        return value
    
    def validate(self, data):
        """Validate date range."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date must be before end date")
        
        return data
