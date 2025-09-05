from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from users.models import TwoFactorCode, User
from users.services import (
    AuthenticationService,
    PermissionService,
    TwoFactorService,
    UserProfileService,
    UserService,
)

User = get_user_model()


class UserServiceTest(TestCase):
    """
    Test cases for UserService.
    """

    def test_create_user(self):
        """Test creating a user with profile."""
        user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role=User.Role.CONTRACTOR,
            phone_number="1234567890",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "test@example.com")
        self.assertEqual(user.role, User.Role.CONTRACTOR)
        self.assertEqual(user.phone_number, "1234567890")
        self.assertTrue(hasattr(user, "profile"))

    def test_update_user_role(self):
        """Test updating user role."""
        user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Update to admin
        updated_user = UserService.update_user_role(user, User.Role.ADMIN)
        self.assertEqual(updated_user.role, User.Role.ADMIN)
        self.assertTrue(updated_user.is_staff)

    def test_update_user_role_invalid(self):
        """Test updating user role with invalid role."""
        user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        with self.assertRaises(ValidationError):
            UserService.update_user_role(user, "invalid_role")

    def test_get_users_by_role(self):
        """Test getting users by role."""
        admin_user = UserService.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN,
        )

        contractor_user = UserService.create_user(
            email="contractor@example.com",
            password="testpass123",
            first_name="Contractor",
            last_name="User",
            role=User.Role.CONTRACTOR,
        )

        admins = UserService.get_users_by_role(User.Role.ADMIN)
        contractors = UserService.get_users_by_role(User.Role.CONTRACTOR)

        self.assertIn(admin_user, admins)
        self.assertNotIn(contractor_user, admins)
        self.assertIn(contractor_user, contractors)
        self.assertNotIn(admin_user, contractors)

    def test_activate_deactivate_user(self):
        """Test activating and deactivating users."""
        user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

        # Deactivate
        deactivated_user = UserService.deactivate_user(user)
        self.assertFalse(deactivated_user.is_active)

        # Activate
        activated_user = UserService.activate_user(user)
        self.assertTrue(activated_user.is_active)


class TwoFactorServiceTest(TestCase):
    """
    Test cases for TwoFactorService.
    """

    def setUp(self):
        self.user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    @patch("users.services.settings.DEBUG", True)
    def test_generate_2fa_code_debug(self):
        """Test 2FA code generation in debug mode."""
        code = TwoFactorService.generate_2fa_code()
        self.assertEqual(code, "123456")

    @patch("users.services.settings.DEBUG", False)
    def test_generate_2fa_code_production(self):
        """Test 2FA code generation in production mode."""
        code = TwoFactorService.generate_2fa_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_create_2fa_code(self):
        """Test creating a 2FA code."""
        code_obj = TwoFactorService.create_2fa_code(self.user)

        self.assertEqual(code_obj.user, self.user)
        self.assertEqual(len(code_obj.code), 6)
        self.assertFalse(code_obj.is_used)
        self.assertFalse(code_obj.is_expired)

    def test_create_2fa_code_invalidates_existing(self):
        """Test that creating a new code invalidates existing ones."""
        # Create first code
        code1 = TwoFactorService.create_2fa_code(self.user)

        # Create second code
        code2 = TwoFactorService.create_2fa_code(self.user)

        # Refresh first code from database
        code1.refresh_from_db()

        self.assertTrue(code1.is_used)
        self.assertFalse(code2.is_used)

    def test_verify_2fa_code_valid(self):
        """Test verifying a valid 2FA code."""
        code_obj = TwoFactorService.create_2fa_code(self.user)

        is_valid = TwoFactorService.verify_2fa_code(self.user, code_obj.code)
        self.assertTrue(is_valid)

        # Code should be marked as used
        code_obj.refresh_from_db()
        self.assertTrue(code_obj.is_used)

    def test_verify_2fa_code_invalid(self):
        """Test verifying an invalid 2FA code."""
        TwoFactorService.create_2fa_code(self.user)

        is_valid = TwoFactorService.verify_2fa_code(self.user, "999999")
        self.assertFalse(is_valid)

    def test_verify_2fa_code_expired(self):
        """Test verifying an expired 2FA code."""
        # Create expired code manually
        expired_code = TwoFactorCode.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        is_valid = TwoFactorService.verify_2fa_code(self.user, expired_code.code)
        self.assertFalse(is_valid)

    def test_enable_disable_2fa(self):
        """Test enabling and disabling 2FA."""
        # Enable 2FA
        success = TwoFactorService.enable_2fa(self.user)
        self.assertTrue(success)
        self.assertTrue(TwoFactorService.is_2fa_enabled(self.user))

        # Disable 2FA
        success = TwoFactorService.disable_2fa(self.user)
        self.assertTrue(success)
        self.assertFalse(TwoFactorService.is_2fa_enabled(self.user))

    @patch("users.services.settings.DEBUG", True)
    @patch("builtins.print")
    def test_send_2fa_code_debug(self, mock_print):
        """Test sending 2FA code in debug mode."""
        TwoFactorService.send_2fa_code(self.user, "123456")
        mock_print.assert_called_once_with(f"2FA Code for {self.user.email}: 123456")


class UserProfileServiceTest(TestCase):
    """
    Test cases for UserProfileService.
    """

    def setUp(self):
        self.user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_or_create_profile(self):
        """Test getting or creating user profile."""
        profile = UserProfileService.get_or_create_profile(self.user)

        self.assertEqual(profile.user, self.user)
        self.assertIsNotNone(profile.id)

        # Getting again should return the same profile
        profile2 = UserProfileService.get_or_create_profile(self.user)
        self.assertEqual(profile.id, profile2.id)

    def test_update_profile(self):
        """Test updating user profile."""
        profile = UserProfileService.update_profile(self.user, bio="Updated bio")

        self.assertEqual(profile.bio, "Updated bio")
        self.assertEqual(profile.user, self.user)


class PermissionServiceTest(TestCase):
    """
    Test cases for PermissionService.
    """

    def setUp(self):
        self.admin_user = UserService.create_user(
            email="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN,
        )

        self.contractor_user = UserService.create_user(
            email="contractor@example.com",
            password="testpass123",
            first_name="Contractor",
            last_name="User",
            role=User.Role.CONTRACTOR,
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
        self.assertFalse(
            PermissionService.can_access_admin_features(self.contractor_user)
        )

    def test_can_create_tickets(self):
        """Test ticket creation permission."""
        self.assertTrue(PermissionService.can_create_tickets(self.admin_user))
        self.assertTrue(PermissionService.can_create_tickets(self.contractor_user))

    def test_can_manage_tickets(self):
        """Test ticket management permission."""
        self.assertTrue(PermissionService.can_manage_tickets(self.admin_user))
        self.assertFalse(PermissionService.can_manage_tickets(self.contractor_user))


class AuthenticationServiceTest(TestCase):
    """
    Test cases for AuthenticationService.
    """

    def setUp(self):
        self.user = UserService.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_authenticate_user_valid(self):
        """Test authenticating with valid credentials."""
        authenticated_user = AuthenticationService.authenticate_user(
            "test@example.com", "testpass123"
        )
        self.assertEqual(authenticated_user, self.user)

    def test_authenticate_user_invalid_credentials(self):
        """Test authenticating with invalid credentials."""
        with self.assertRaises(ValidationError):
            AuthenticationService.authenticate_user("test@example.com", "wrongpassword")

    def test_authenticate_user_inactive(self):
        """Test authenticating inactive user."""
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(ValidationError):
            AuthenticationService.authenticate_user("test@example.com", "testpass123")

    def test_check_login_attempts(self):
        """Test login attempts check."""
        # Currently always returns True, but test the interface
        result = AuthenticationService.check_login_attempts("test@example.com")
        self.assertTrue(result)
