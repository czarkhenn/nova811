import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from ..models import Ticket, UserLog, TicketLog

User = get_user_model()


@pytest.mark.django_db
class TestTicketModel:
    """Test cases for the Ticket model."""

    def test_create_ticket_with_required_fields(self):
        """Test creating a ticket with all required fields."""
        # Create users
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            first_name="Contractor",
            last_name="User",
            role=User.Role.CONTRACTOR
        )
        
        # Create ticket
        expiration_date = timezone.now() + timedelta(days=30)
        ticket = Ticket.objects.create(
            organization="Test Organization",
            location="Test Location",
            expiration_date=expiration_date,
            notes="Test notes",
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        assert ticket.organization == "Test Organization"
        assert ticket.location == "Test Location"
        assert ticket.status == Ticket.Status.OPEN
        assert ticket.assigned_contractor == contractor
        assert ticket.created_by == admin
        assert ticket.updated_by == admin
        assert ticket.ticket_number is not None
        assert ticket.ticket_number.startswith("TKT-")

    def test_ticket_number_generation(self):
        """Test that ticket numbers are generated correctly."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        expiration_date = timezone.now() + timedelta(days=30)
        
        # Create first ticket
        ticket1 = Ticket.objects.create(
            organization="Test Org 1",
            location="Location 1",
            expiration_date=expiration_date,
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        # Create second ticket
        ticket2 = Ticket.objects.create(
            organization="Test Org 2",
            location="Location 2",
            expiration_date=expiration_date,
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        # Check ticket numbers are unique and sequential
        assert ticket1.ticket_number != ticket2.ticket_number
        assert ticket1.ticket_number.startswith("TKT-")
        assert ticket2.ticket_number.startswith("TKT-")
        
        # Extract sequence numbers
        seq1 = int(ticket1.ticket_number.split('-')[-1])
        seq2 = int(ticket2.ticket_number.split('-')[-1])
        assert seq2 == seq1 + 1

    def test_ticket_expiration_properties(self):
        """Test ticket expiration-related properties."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        # Test expired ticket
        expired_date = timezone.now() - timedelta(days=1)
        expired_ticket = Ticket.objects.create(
            organization="Expired Org",
            location="Location",
            expiration_date=expired_date,
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        assert expired_ticket.is_expired is True
        assert expired_ticket.is_expiring_soon is True  # Expired tickets are also "expiring soon"
        
        # Test expiring soon ticket
        expiring_date = timezone.now() + timedelta(hours=24)
        expiring_ticket = Ticket.objects.create(
            organization="Expiring Org",
            location="Location",
            expiration_date=expiring_date,
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        assert expiring_ticket.is_expired is False
        assert expiring_ticket.is_expiring_soon is True
        
        # Test normal ticket
        future_date = timezone.now() + timedelta(days=30)
        normal_ticket = Ticket.objects.create(
            organization="Normal Org",
            location="Location",
            expiration_date=future_date,
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        assert normal_ticket.is_expired is False
        assert normal_ticket.is_expiring_soon is False

    def test_ticket_renew_method(self):
        """Test the ticket renewal method."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        original_expiration = timezone.now() + timedelta(days=10)
        ticket = Ticket.objects.create(
            organization="Test Org",
            location="Location",
            expiration_date=original_expiration,
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        # Renew ticket
        ticket.renew(renewed_by=admin, days=15)
        
        # Check expiration date was extended
        expected_expiration = original_expiration + timedelta(days=15)
        assert ticket.expiration_date == expected_expiration
        assert ticket.updated_by == admin

    def test_ticket_str_representation(self):
        """Test ticket string representation."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        ticket = Ticket.objects.create(
            organization="Test Organization",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        expected = f"{ticket.ticket_number} - Test Organization"
        assert str(ticket) == expected


@pytest.mark.django_db
class TestUserLogModel:
    """Test cases for the UserLog model."""

    def test_create_user_log(self):
        """Test creating a user log entry."""
        user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        log = UserLog.objects.create(
            user=user,
            action=UserLog.Action.LOGIN,
            details={"test": "data"},
            ip_address="192.168.1.1"
        )
        
        assert log.user == user
        assert log.action == UserLog.Action.LOGIN
        assert log.details == {"test": "data"}
        assert log.ip_address == "192.168.1.1"
        assert log.timestamp is not None

    def test_user_log_with_related_ticket(self):
        """Test creating a user log with related ticket."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        ticket = Ticket.objects.create(
            organization="Test Org",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        log = UserLog.objects.create(
            user=admin,
            action=UserLog.Action.TICKET_CREATED,
            details={"ticket_id": str(ticket.id)},
            related_ticket=ticket
        )
        
        assert log.related_ticket == ticket
        assert log.action == UserLog.Action.TICKET_CREATED

    def test_user_log_str_representation(self):
        """Test user log string representation."""
        user = User.objects.create_user(
            email="user@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        log = UserLog.objects.create(
            user=user,
            action=UserLog.Action.LOGIN
        )
        
        expected = f"{user.email} - {log.get_action_display()} - {log.timestamp}"
        assert str(log) == expected


@pytest.mark.django_db
class TestTicketLogModel:
    """Test cases for the TicketLog model."""

    def test_create_ticket_log(self):
        """Test creating a ticket log entry."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        ticket = Ticket.objects.create(
            organization="Test Org",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        log = TicketLog.objects.create(
            ticket=ticket,
            action_by=admin,
            action=TicketLog.Action.CREATED,
            details={"organization": "Test Org"},
            previous_values={}
        )
        
        assert log.ticket == ticket
        assert log.action_by == admin
        assert log.action == TicketLog.Action.CREATED
        assert log.details == {"organization": "Test Org"}
        assert log.previous_values == {}
        assert log.timestamp is not None

    def test_ticket_log_system_action(self):
        """Test creating a ticket log for system actions."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        ticket = Ticket.objects.create(
            organization="Test Org",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        # System action (no action_by user)
        log = TicketLog.objects.create(
            ticket=ticket,
            action_by=None,
            action=TicketLog.Action.CLOSED,
            details={"reason": "Automatically closed due to expiration"}
        )
        
        assert log.ticket == ticket
        assert log.action_by is None
        assert log.action == TicketLog.Action.CLOSED

    def test_ticket_log_str_representation(self):
        """Test ticket log string representation."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        ticket = Ticket.objects.create(
            organization="Test Org",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        log = TicketLog.objects.create(
            ticket=ticket,
            action_by=admin,
            action=TicketLog.Action.CREATED
        )
        
        expected = f"{ticket.ticket_number} - {log.get_action_display()} by {admin.email}"
        assert str(log) == expected


@pytest.mark.django_db
class TestTicketModelConstraints:
    """Test model constraints and validations."""

    def test_ticket_status_choices(self):
        """Test that ticket status choices are correctly defined."""
        assert Ticket.Status.OPEN == "open"
        assert Ticket.Status.IN_PROGRESS == "in_progress"
        assert Ticket.Status.CLOSED == "closed"
        
        choices = Ticket.Status.choices
        assert ("open", "Open") in choices
        assert ("in_progress", "In Progress") in choices
        assert ("closed", "Closed") in choices

    def test_user_log_action_choices(self):
        """Test that user log action choices are correctly defined."""
        assert UserLog.Action.LOGIN == "login"
        assert UserLog.Action.TICKET_CREATED == "ticket_created"
        assert UserLog.Action.TICKET_RENEWED == "ticket_renewed"
        
        choices = UserLog.Action.choices
        assert ("login", "Login") in choices
        assert ("ticket_created", "Ticket Created") in choices

    def test_ticket_log_action_choices(self):
        """Test that ticket log action choices are correctly defined."""
        assert TicketLog.Action.CREATED == "created"
        assert TicketLog.Action.UPDATED == "updated"
        assert TicketLog.Action.RENEWED == "renewed"
        
        choices = TicketLog.Action.choices
        assert ("created", "Created") in choices
        assert ("updated", "Updated") in choices
        assert ("renewed", "Renewed") in choices

    def test_ticket_ordering(self):
        """Test that tickets are ordered by creation date descending."""
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        
        # Create tickets with slight time difference
        ticket1 = Ticket.objects.create(
            organization="First Org",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        ticket2 = Ticket.objects.create(
            organization="Second Org",
            location="Location",
            expiration_date=timezone.now() + timedelta(days=30),
            assigned_contractor=contractor,
            created_by=admin,
            updated_by=admin
        )
        
        # Get all tickets (should be ordered by created_date desc)
        tickets = list(Ticket.objects.all())
        assert tickets[0] == ticket2  # Most recent first
        assert tickets[1] == ticket1
