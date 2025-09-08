"""
Tests business logic in services layer.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from users.services import UserService, PermissionService

User = get_user_model()


class TestUserService(TestCase):
    """Test UserService business logic."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            role=User.Role.ADMIN
        )
        self.contractor_user = User.objects.create_user(
            email='contractor@example.com',
            password='testpass123',
            role=User.Role.CONTRACTOR
        )

    def test_update_user_role_valid(self):
        """Test updating user role with valid role."""
        updated_user = UserService.update_user_role(
            self.contractor_user, 
            User.Role.ADMIN
        )
        
        self.assertEqual(updated_user.role, User.Role.ADMIN)
        self.assertTrue(updated_user.is_staff)

    def test_update_user_role_invalid(self):
        """Test updating user role with invalid role."""
        with self.assertRaises(ValidationError):
            UserService.update_user_role(self.contractor_user, 'invalid_role')

    def test_bulk_update_user_status(self):
        """Test bulk updating user active status."""
        user_ids = [self.admin_user.id, self.contractor_user.id]
        updated_count = UserService.bulk_update_user_status(user_ids, False)
        
        self.assertEqual(updated_count, 2)
        
        # Refresh from database
        self.admin_user.refresh_from_db()
        self.contractor_user.refresh_from_db()
        
        self.assertFalse(self.admin_user.is_active)
        self.assertFalse(self.contractor_user.is_active)

    def test_get_user_statistics(self):
        """Test getting user statistics."""
        stats = UserService.get_user_statistics()
        
        expected_stats = {
            'total_users': 2,
            'admin_users': 1,
            'contractor_users': 1,
            'active_users': 2,
            'inactive_users': 0,
        }
        
        self.assertEqual(stats, expected_stats)


class TestPermissionService(TestCase):
    """Test PermissionService business logic."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            role=User.Role.ADMIN
        )
        self.contractor_user = User.objects.create_user(
            email='contractor@example.com',
            password='testpass123',
            role=User.Role.CONTRACTOR
        )

    def test_is_admin(self):
        """Test admin role check."""
        self.assertTrue(PermissionService.is_admin(self.admin_user))
        self.assertFalse(PermissionService.is_admin(self.contractor_user))

    def test_is_contractor(self):
        """Test contractor role check."""
        self.assertFalse(PermissionService.is_contractor(self.admin_user))
        self.assertTrue(PermissionService.is_contractor(self.contractor_user))

    def test_can_manage_users(self):
        """Test user management permission."""
        self.assertTrue(PermissionService.can_manage_users(self.admin_user))
        self.assertFalse(PermissionService.can_manage_users(self.contractor_user))

    def test_can_access_admin_features(self):
        """Test admin features access permission."""
        self.assertTrue(PermissionService.can_access_admin_features(self.admin_user))
        self.assertFalse(PermissionService.can_access_admin_features(self.contractor_user))

    def test_can_view_user_stats(self):
        """Test user stats viewing permission."""
        self.assertTrue(PermissionService.can_view_user_stats(self.admin_user))
        self.assertFalse(PermissionService.can_view_user_stats(self.contractor_user))

    def test_can_create_tickets(self):
        """Test ticket creation permission."""
        self.assertTrue(PermissionService.can_create_tickets(self.admin_user))
        self.assertTrue(PermissionService.can_create_tickets(self.contractor_user))

    def test_can_manage_tickets(self):
        """Test ticket management permission."""
        self.assertTrue(PermissionService.can_manage_tickets(self.admin_user))
        self.assertFalse(PermissionService.can_manage_tickets(self.contractor_user))
