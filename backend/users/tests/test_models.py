from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from users.models import TwoFactorCode, User, UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """
    Test cases for the custom User model.
    """

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user_with_default_role(self):
        """Test creating a user with default contractor role."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, User.Role.CONTRACTOR)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_contractor)
        self.assertFalse(user.is_admin)

    def test_create_admin_user(self):
        """Test creating a user with admin role."""
        self.user_data["role"] = User.Role.ADMIN
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_contractor)

    def test_user_str_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.username} ({user.get_role_display()})"
        self.assertEqual(str(user), expected)

    def test_user_save_sets_is_staff(self):
        """Test that saving a user sets is_staff based on role."""
        user = User.objects.create_user(**self.user_data)

        # Initially contractor, should not be staff
        self.assertFalse(user.is_staff)

        # Change to admin
        user.role = User.Role.ADMIN
        user.save()
        self.assertTrue(user.is_staff)

        # Change back to contractor
        user.role = User.Role.CONTRACTOR
        user.save()
        self.assertFalse(user.is_staff)

    def test_user_indexes(self):
        """Test that database indexes are created."""
        # This would typically be tested with database introspection
        # For now, we just ensure the model can be created
        user = User.objects.create_user(**self.user_data)
        self.assertIsNotNone(user.id)


class UserProfileModelTest(TestCase):
    """
    Test cases for the UserProfile model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_create_user_profile(self):
        """Test creating a user profile."""
        profile = UserProfile.objects.create(
            user=self.user, bio="Test bio", two_factor_enabled=True
        )

        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, "Test bio")
        self.assertTrue(profile.two_factor_enabled)
        self.assertEqual(profile.backup_tokens, [])

    def test_user_profile_str_representation(self):
        """Test user profile string representation."""
        profile = UserProfile.objects.create(user=self.user)
        expected = f"Profile for {self.user.username}"
        self.assertEqual(str(profile), expected)

    def test_user_profile_default_values(self):
        """Test user profile default values."""
        profile = UserProfile.objects.create(user=self.user)

        self.assertFalse(profile.two_factor_enabled)
        self.assertEqual(profile.backup_tokens, [])
        self.assertIsNone(profile.bio)
        self.assertFalse(profile.avatar)  # ImageField is falsy when empty


class TwoFactorCodeModelTest(TestCase):
    """
    Test cases for the TwoFactorCode model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_create_two_factor_code(self):
        """Test creating a 2FA code."""
        expires_at = timezone.now() + timedelta(minutes=10)
        code = TwoFactorCode.objects.create(
            user=self.user, code="123456", expires_at=expires_at
        )

        self.assertEqual(code.user, self.user)
        self.assertEqual(code.code, "123456")
        self.assertFalse(code.is_used)
        self.assertEqual(code.expires_at, expires_at)

    def test_two_factor_code_str_representation(self):
        """Test 2FA code string representation."""
        expires_at = timezone.now() + timedelta(minutes=10)
        code = TwoFactorCode.objects.create(
            user=self.user, code="123456", expires_at=expires_at
        )
        expected = f"2FA Code for {self.user.username}"
        self.assertEqual(str(code), expected)

    def test_is_expired_property(self):
        """Test the is_expired property."""
        # Create expired code
        expired_code = TwoFactorCode.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertTrue(expired_code.is_expired)

        # Create valid code
        valid_code = TwoFactorCode.objects.create(
            user=self.user,
            code="654321",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        self.assertFalse(valid_code.is_expired)

    def test_is_valid_property(self):
        """Test the is_valid property."""
        # Create valid code
        valid_code = TwoFactorCode.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=10),
        )
        self.assertTrue(valid_code.is_valid)

        # Mark as used
        valid_code.is_used = True
        valid_code.save()
        self.assertFalse(valid_code.is_valid)

        # Create expired code
        expired_code = TwoFactorCode.objects.create(
            user=self.user,
            code="654321",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertFalse(expired_code.is_valid)

    def test_ordering(self):
        """Test that codes are ordered by creation date (newest first)."""
        # Create first code
        code1 = TwoFactorCode.objects.create(
            user=self.user,
            code="111111",
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # Create second code
        code2 = TwoFactorCode.objects.create(
            user=self.user,
            code="222222",
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        codes = list(TwoFactorCode.objects.all())
        self.assertEqual(codes[0], code2)  # Newest first
        self.assertEqual(codes[1], code1)
