import pytest
import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from tickets.models import Ticket
from users.models import User

User = get_user_model()


@pytest.mark.django_db
class TestTicketAPI:
    """Test cases for Ticket API endpoints with role-based access control."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test data."""
        # Create users
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
        
        # Create tickets
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
        
        # Set up API client
        self.client = APIClient()

    def test_admin_can_list_all_tickets(self):
        """Test that admin users can list all tickets."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data (paginated format)
        data = response.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 3
        assert len(data['results']) == 3
        
        # Verify all tickets are included
        ticket_numbers = [ticket['ticket_number'] for ticket in data['results']]
        assert self.ticket1.ticket_number in ticket_numbers
        assert self.ticket2.ticket_number in ticket_numbers
        assert self.ticket3.ticket_number in ticket_numbers

    def test_contractor_can_see_only_assigned_tickets(self):
        """Test that contractor users can only see their assigned tickets."""
        # Test contractor1 - should see ticket1 and ticket3
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data (paginated format)
        data = response.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 2
        assert len(data['results']) == 2
        
        ticket_numbers = [ticket['ticket_number'] for ticket in data['results']]
        assert self.ticket1.ticket_number in ticket_numbers
        assert self.ticket3.ticket_number in ticket_numbers
        assert self.ticket2.ticket_number not in ticket_numbers

    def test_contractor2_can_see_only_their_tickets(self):
        """Test that contractor2 can only see their assigned tickets."""
        # Test contractor2 - should see only ticket2
        self.client.force_authenticate(user=self.contractor2)
        
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data (paginated format)
        data = response.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 1
        assert len(data['results']) == 1
        
        ticket_numbers = [ticket['ticket_number'] for ticket in data['results']]
        assert self.ticket2.ticket_number in ticket_numbers
        assert self.ticket1.ticket_number not in ticket_numbers
        assert self.ticket3.ticket_number not in ticket_numbers

    def test_unauthenticated_user_cannot_access_tickets(self):
        """Test that unauthenticated users cannot access tickets."""
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_can_get_ticket_by_id(self):
        """Test that admin can access any ticket by ID."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-detail', kwargs={'ticket_id': self.ticket1.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['ticket_number'] == self.ticket1.ticket_number
        assert data['organization'] == self.ticket1.organization

    def test_contractor_can_access_assigned_ticket_by_id(self):
        """Test that contractor can access their assigned ticket by ID."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-detail', kwargs={'ticket_id': self.ticket1.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['ticket_number'] == self.ticket1.ticket_number

    def test_contractor_cannot_access_other_contractor_ticket(self):
        """Test that contractor cannot access other contractor's tickets."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-detail', kwargs={'ticket_id': self.ticket2.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_can_get_ticket_stats(self):
        """Test that admin can get ticket statistics."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-stats')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['total'] == 3
        assert data['open'] == 1
        assert data['in_progress'] == 1
        assert data['closed'] == 1

    def test_contractor_can_get_their_ticket_stats(self):
        """Test that contractor can get their ticket statistics."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-stats')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data['total'] == 2
        assert data['open'] == 1
        assert data['in_progress'] == 0
        assert data['closed'] == 1

    def test_admin_can_get_contractors_list(self):
        """Test that admin can get list of contractors."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:contractor-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2  # contractor1 and contractor2
        
        emails = [contractor['email'] for contractor in data]
        assert self.contractor1.email in emails
        assert self.contractor2.email in emails

    def test_contractor_cannot_get_contractors_list(self):
        """Test that contractor cannot get list of contractors."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:contractor-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tickets_with_status_filter(self):
        """Test filtering tickets by status."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url, {'status': 'open'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data (paginated format)
        data = response.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 1
        assert len(data['results']) == 1
        assert data['results'][0]['status'] == 'open'

    def test_tickets_with_search_filter(self):
        """Test filtering tickets by search term."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url, {'search': 'Test Org 1'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data (paginated format)
        data = response.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 1
        assert len(data['results']) == 1
        assert data['results'][0]['organization'] == 'Test Org 1'

    def test_contractor_with_status_filter(self):
        """Test contractor filtering their tickets by status."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-list-create')
        response = self.client.get(url, {'status': 'open'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data (paginated format)
        data = response.json()
        assert 'count' in data
        assert 'results' in data
        assert data['count'] == 1
        assert len(data['results']) == 1
        assert data['results'][0]['status'] == 'open'
        assert data['results'][0]['ticket_number'] == self.ticket1.ticket_number

    def test_dashboard_data_for_admin(self):
        """Test dashboard data for admin user."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:dashboard')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'ticket_stats' in data
        assert 'recent_tickets' in data
        assert 'expiring_tickets' in data
        assert 'recent_activity' in data

    def test_dashboard_data_for_contractor(self):
        """Test dashboard data for contractor user."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:dashboard')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'ticket_stats' in data
        assert 'recent_tickets' in data
        assert 'expiring_tickets' in data
        assert 'recent_activity' in data

    def test_user_logs_for_admin(self):
        """Test user logs for admin user."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:user-logs')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'count' in data
        assert 'results' in data

    def test_user_logs_for_contractor(self):
        """Test user logs for contractor user."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:user-logs')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'count' in data
        assert 'results' in data

    def test_ticket_logs_for_admin(self):
        """Test ticket logs for admin user."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-logs')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'count' in data
        assert 'results' in data

    def test_ticket_logs_for_contractor(self):
        """Test ticket logs for contractor user."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-logs')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert 'count' in data
        assert 'results' in data

    def test_api_endpoints_return_json(self):
        """Test that all API endpoints return valid JSON."""
        self.client.force_authenticate(user=self.admin_user)
        
        endpoints = [
            reverse('tickets:ticket-list-create'),
            reverse('tickets:ticket-stats'),
            reverse('tickets:contractor-list'),
            reverse('tickets:dashboard'),
            reverse('tickets:user-logs'),
            reverse('tickets:ticket-logs'),
        ]
        
        for url in endpoints:
            response = self.client.get(url)
            assert response.status_code == status.HTTP_200_OK
            
            # Verify it's valid JSON
            try:
                json.loads(response.content)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON response from {url}")

    def test_admin_can_assign_ticket_to_contractor(self):
        """Test that admin can assign ticket to a contractor."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Assign ticket1 (currently assigned to contractor1) to contractor2
        url = reverse('tickets:ticket-assign', kwargs={'ticket_id': self.ticket1.id})
        data = {'assigned_contractor_id': self.contractor2.id}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the assignment was successful
        response_data = response.json()
        assert 'message' in response_data
        assert 'ticket' in response_data
        assert response_data['ticket']['assigned_contractor']['id'] == self.contractor2.id
        
        # Verify in database
        self.ticket1.refresh_from_db()
        assert self.ticket1.assigned_contractor.id == self.contractor2.id

    def test_contractor_cannot_assign_ticket(self):
        """Test that contractor cannot assign tickets."""
        self.client.force_authenticate(user=self.contractor1)
        
        url = reverse('tickets:ticket-assign', kwargs={'ticket_id': self.ticket1.id})
        data = {'assigned_contractor_id': self.contractor2.id}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assign_ticket_with_invalid_contractor(self):
        """Test assigning ticket with invalid contractor ID."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-assign', kwargs={'ticket_id': self.ticket1.id})
        data = {'assigned_contractor_id': 99999}  # Non-existent contractor
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_assign_nonexistent_ticket(self):
        """Test assigning non-existent ticket."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:ticket-assign', kwargs={'ticket_id': '00000000-0000-0000-0000-000000000000'})
        data = {'assigned_contractor_id': self.contractor2.id}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_contractors_list_contains_required_fields(self):
        """Test that contractors list contains all required fields for assignment."""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('tickets:contractor-list')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Check that each contractor has required fields
        for contractor in data:
            assert 'id' in contractor
            assert 'first_name' in contractor
            assert 'last_name' in contractor
            assert 'email' in contractor
            assert contractor['id'] is not None
            assert contractor['first_name'] is not None
            assert contractor['last_name'] is not None
            assert contractor['email'] is not None

    def test_role_based_access_consistency(self):
        """Test that role-based access is consistent across all endpoints."""
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        
        admin_endpoints = [
            reverse('tickets:ticket-list-create'),
            reverse('tickets:ticket-stats'),
            reverse('tickets:contractor-list'),
            reverse('tickets:dashboard'),
        ]
        
        for url in admin_endpoints:
            response = self.client.get(url)
            assert response.status_code == status.HTTP_200_OK, f"Admin should access {url}"
        
        # Test contractor access
        self.client.force_authenticate(user=self.contractor1)
        
        contractor_allowed_endpoints = [
            reverse('tickets:ticket-list-create'),
            reverse('tickets:ticket-stats'),
            reverse('tickets:dashboard'),
        ]
        
        for url in contractor_allowed_endpoints:
            response = self.client.get(url)
            assert response.status_code == status.HTTP_200_OK, f"Contractor should access {url}"
        
        # Test contractor forbidden endpoints
        contractor_forbidden_endpoints = [
            reverse('tickets:contractor-list'),
        ]
        
        for url in contractor_forbidden_endpoints:
            response = self.client.get(url)
            assert response.status_code == status.HTTP_403_FORBIDDEN, f"Contractor should not access {url}"
