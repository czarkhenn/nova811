import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from ..models import Ticket, UserLog, TicketLog
from ..serializers import (
    TicketLogOutputSerializer,
    UserLogOutputSerializer,
    TicketBasicOutputSerializer,
    UserBasicOutputSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestTicketSerializers:
    """Test ticket-related serializers."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN
        )
        
        self.contractor_user = User.objects.create_user(
            email='contractor@test.com',
            password='testpass123',
            first_name='John',
            last_name='Contractor',
            role=User.Role.CONTRACTOR
        )
        
        self.ticket = Ticket.objects.create(
            organization='Test Org',
            location='Test Location',
            status=Ticket.Status.OPEN,
            expiration_date=timezone.now() + timedelta(days=30),
            notes='Test notes',
            assigned_contractor=self.contractor_user,
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
    
    def test_ticket_basic_output_serializer(self):
        """Test TicketBasicOutputSerializer."""
        serializer = TicketBasicOutputSerializer(self.ticket)
        data = serializer.data
        
        assert data['ticket_number'] == self.ticket.ticket_number
        assert data['organization'] == 'Test Org'
        assert data['status'] == 'open'
    
    def test_user_basic_output_serializer(self):
        """Test UserBasicOutputSerializer."""
        serializer = UserBasicOutputSerializer(self.admin_user)
        data = serializer.data
        
        assert data['email'] == 'admin@test.com'
        assert data['first_name'] == 'Admin'
        assert data['last_name'] == 'User'
        assert data['role'] == 'admin'
    
    def test_user_log_output_serializer(self):
        """Test UserLogOutputSerializer with display names."""
        user_log = UserLog.objects.create(
            user=self.admin_user,
            action=UserLog.Action.LOGIN,
            details={'ip_address': '127.0.0.1'},
            ip_address='127.0.0.1',
            related_ticket=self.ticket
        )
        
        serializer = UserLogOutputSerializer(user_log)
        data = serializer.data
        
        assert data['action'] == 'login'
        assert data['action_display'] == 'Login'
        
        assert data['user']['email'] == 'admin@test.com'
        assert data['user']['first_name'] == 'Admin'
        
        assert data['related_ticket']['ticket_number'] == self.ticket.ticket_number
        assert data['related_ticket']['organization'] == 'Test Org'
    
    def test_ticket_log_output_serializer(self):
        """Test TicketLogOutputSerializer with display names."""
        ticket_log = TicketLog.objects.create(
            ticket=self.ticket,
            action_by=self.admin_user,
            action=TicketLog.Action.CREATED,
            details={'reason': 'Initial creation'},
            previous_values={}
        )
        
        serializer = TicketLogOutputSerializer(ticket_log)
        data = serializer.data
        
        assert data['action'] == 'created'
        assert data['action_display'] == 'Created'
        
        assert data['action_by']['email'] == 'admin@test.com'
        assert data['action_by']['first_name'] == 'Admin'
        
        assert data['ticket']['ticket_number'] == self.ticket.ticket_number
        assert data['ticket']['organization'] == 'Test Org'
        assert data['ticket']['status'] == 'open'
    
    def test_user_log_without_related_ticket(self):
        """Test UserLogOutputSerializer without related ticket."""
        user_log = UserLog.objects.create(
            user=self.admin_user,
            action=UserLog.Action.PROFILE_UPDATE,
            details={'field': 'email'},
            ip_address='127.0.0.1'
        )
        
        serializer = UserLogOutputSerializer(user_log)
        data = serializer.data
        
        assert data['action_display'] == 'Profile Update'
        assert data['related_ticket'] is None
    
    def test_ticket_log_without_action_by(self):
        """Test TicketLogOutputSerializer without action_by (system action)."""
        ticket_log = TicketLog.objects.create(
            ticket=self.ticket,
            action_by=None,
            action=TicketLog.Action.UPDATED,
            details={'system': 'auto-update'},
            previous_values={'status': 'open'}
        )
        
        serializer = TicketLogOutputSerializer(ticket_log)
        data = serializer.data
        
        assert data['action_display'] == 'Updated'
        assert data['action_by'] is None
        assert data['ticket']['ticket_number'] == self.ticket.ticket_number


@pytest.mark.django_db
class TestLogDisplayNames:
    """Test that log display names are working correctly."""
    
    def test_user_log_action_choices(self):
        """Test that UserLog action choices have proper display names."""
        choices = UserLog.Action.choices
        
        choice_dict = dict(choices)
        assert choice_dict['login'] == 'Login'
        assert choice_dict['logout'] == 'Logout'
        assert choice_dict['ticket_created'] == 'Ticket Created'
        assert choice_dict['ticket_updated'] == 'Ticket Updated'
        assert choice_dict['two_factor_enable'] == '2FA Enable'
    
    def test_ticket_log_action_choices(self):
        """Test that TicketLog action choices have proper display names."""
        choices = TicketLog.Action.choices
        
        choice_dict = dict(choices)
        assert choice_dict['created'] == 'Created'
        assert choice_dict['updated'] == 'Updated'
        assert choice_dict['status_changed'] == 'Status Changed'
        assert choice_dict['assigned'] == 'Assigned'
        assert choice_dict['renewed'] == 'Renewed'
        assert choice_dict['closed'] == 'Closed'
    
    def test_ticket_status_choices(self):
        """Test that Ticket status choices have proper display names."""
        choices = Ticket.Status.choices
        
        choice_dict = dict(choices)
        assert choice_dict['open'] == 'Open'
        assert choice_dict['in_progress'] == 'In Progress'
        assert choice_dict['closed'] == 'Closed'
