import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from tickets.models import Ticket
from tickets.selectors import TicketSelector

User = get_user_model()


@pytest.mark.django_db
class TestTicketSelector:
    """Test cases for TicketSelector with role-based access control."""

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
        
        self.contractor1 = User.objects.create_user(
            email='contractor1@test.com',
            password='testpass123',
            first_name='Contractor',
            last_name='One',
            role=User.Role.CONTRACTOR
        )
        
        self.contractor2 = User.objects.create_user(
            email='contractor2@test.com',
            password='testpass123',
            first_name='Contractor',
            last_name='Two',
            role=User.Role.CONTRACTOR
        )
        
        self.ticket1 = Ticket.objects.create(
            organization='Test Org 1',
            location='Location 1',
            assigned_contractor=self.contractor1,
            created_by=self.admin_user,
            updated_by=self.admin_user,
            expiration_date=timezone.now() + timedelta(days=7),
            status=Ticket.Status.OPEN
        )
        
        self.ticket2 = Ticket.objects.create(
            organization='Test Org 2',
            location='Location 2',
            assigned_contractor=self.contractor2,
            created_by=self.admin_user,
            updated_by=self.admin_user,
            expiration_date=timezone.now() + timedelta(days=5),
            status=Ticket.Status.IN_PROGRESS
        )
        
        self.ticket3 = Ticket.objects.create(
            organization='Test Org 3',
            location='Location 3',
            assigned_contractor=self.contractor1,
            created_by=self.admin_user,
            updated_by=self.admin_user,
            expiration_date=timezone.now() + timedelta(days=3),
            status=Ticket.Status.CLOSED
        )

    def test_admin_can_see_all_tickets(self):
        """Test that admin users can see all tickets."""
        tickets = TicketSelector.get_tickets_for_user(self.admin_user)
        assert tickets.count() == 3
        
        ticket_ids = list(tickets.values_list('id', flat=True))
        assert self.ticket1.id in ticket_ids
        assert self.ticket2.id in ticket_ids
        assert self.ticket3.id in ticket_ids

    def test_contractor_can_see_only_assigned_tickets(self):
        """Test that contractor users can only see their assigned tickets."""
        tickets1 = TicketSelector.get_tickets_for_user(self.contractor1)
        assert tickets1.count() == 2
        
        ticket_ids1 = list(tickets1.values_list('id', flat=True))
        assert self.ticket1.id in ticket_ids1
        assert self.ticket3.id in ticket_ids1
        assert self.ticket2.id not in ticket_ids1
        
        tickets2 = TicketSelector.get_tickets_for_user(self.contractor2)
        assert tickets2.count() == 1
        
        ticket_ids2 = list(tickets2.values_list('id', flat=True))
        assert self.ticket2.id in ticket_ids2
        assert self.ticket1.id not in ticket_ids2
        assert self.ticket3.id not in ticket_ids2

    def test_user_role_properties(self):
        """Test that user role properties work correctly."""
        assert self.admin_user.is_admin is True
        assert self.admin_user.is_contractor is False
        assert self.admin_user.role == User.Role.ADMIN
        
        assert self.contractor1.is_admin is False
        assert self.contractor1.is_contractor is True
        assert self.contractor1.role == User.Role.CONTRACTOR

    def test_get_ticket_by_id_admin_access(self):
        """Test that admin can access any ticket by ID."""
        ticket = TicketSelector.get_ticket_by_id(self.ticket1.id, self.admin_user)
        assert ticket is not None
        assert ticket.id == self.ticket1.id
        
        ticket = TicketSelector.get_ticket_by_id(self.ticket2.id, self.admin_user)
        assert ticket is not None
        assert ticket.id == self.ticket2.id

    def test_get_ticket_by_id_contractor_access(self):
        """Test that contractor can only access their assigned tickets."""
        ticket = TicketSelector.get_ticket_by_id(self.ticket1.id, self.contractor1)
        assert ticket is not None
        assert ticket.id == self.ticket1.id
        
        ticket = TicketSelector.get_ticket_by_id(self.ticket2.id, self.contractor1)
        assert ticket is None

    def test_get_ticket_stats_for_admin(self):
        """Test ticket stats for admin user."""
        stats = TicketSelector.get_ticket_stats_for_user(self.admin_user)
        
        assert stats['total'] == 3
        assert stats['open'] == 1
        assert stats['in_progress'] == 1
        assert stats['closed'] == 1

    def test_get_ticket_stats_for_contractor(self):
        """Test ticket stats for contractor user."""
        stats = TicketSelector.get_ticket_stats_for_user(self.contractor1)
        
        assert stats['total'] == 2
        assert stats['open'] == 1
        assert stats['in_progress'] == 0
        assert stats['closed'] == 1

    def test_tickets_with_status_filter(self):
        """Test filtering tickets by status."""
        open_tickets = TicketSelector.get_tickets_for_user(
            self.admin_user, 
            status=Ticket.Status.OPEN
        )
        assert open_tickets.count() == 1
        
        open_tickets_contractor = TicketSelector.get_tickets_for_user(
            self.contractor1, 
            status=Ticket.Status.OPEN
        )
        assert open_tickets_contractor.count() == 1

    def test_tickets_with_search_filter(self):
        """Test filtering tickets by search term."""
        search_tickets = TicketSelector.get_tickets_for_user(
            self.admin_user, 
            search='Test Org 1'
        )
        assert search_tickets.count() == 1
        assert search_tickets.first().id == self.ticket1.id
