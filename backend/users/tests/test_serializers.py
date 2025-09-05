from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.test import APIRequestFactory
from users.models import User, UserProfile
from users.serializers import (
    PasswordChangeSerializer,
    TwoFactorMethodSerializer,
    TwoFactorSetupSerializer,
    TwoFactorStatusSerializer,
    TwoFactorVerifySerializer,
    UserCreateSerializer,
    UserDetailsSerializer,
    UserProfileSerializer,
    UserWithProfileSerializer,
)
from users.services import UserProfileService, UserService

User = get_user_model()


@pytest.fixture
def user():
    """Fixture for a test user."""
    return UserService.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        role=User.Role.CONTRACTOR,
        phone_number="1234567890",
    )


@pytest.fixture
def admin_user():
    """Fixture for an admin user."""
    return UserService.create_user(
        email="admin@example.com",
        password="testpass123",
        first_name="Admin",
        last_name="User",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def request_factory():
    """Fixture for API request factory."""
    return APIRequestFactory()


@pytest.mark.django_db
class TestUserDetailsSerializer:
    """Test cases for UserDetailsSerializer."""

    def test_serialize_user_details(self, user):
        """Test serializing user details."""
        serializer = UserDetailsSerializer(user)
        data = serializer.data

        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert data["role"] == user.role
        assert data["role_display"] == user.get_role_display()
        assert data["phone_number"] == user.phone_number
        assert data["is_admin"] == user.is_admin
        assert data["is_contractor"] == user.is_contractor
        assert data["is_active"] == user.is_active

    def test_admin_user_properties(self, admin_user):
        """Test admin user properties in serialization."""
        serializer = UserDetailsSerializer(admin_user)
        data = serializer.data

        assert data["is_admin"] is True
        assert data["is_contractor"] is False
        assert data["role"] == User.Role.ADMIN

    def test_contractor_user_properties(self, user):
        """Test contractor user properties in serialization."""
        serializer = UserDetailsSerializer(user)
        data = serializer.data

        assert data["is_admin"] is False
        assert data["is_contractor"] is True
        assert data["role"] == User.Role.CONTRACTOR

    def test_read_only_fields(self, user):
        """Test that read-only fields cannot be updated."""
        serializer = UserDetailsSerializer(user, data={"is_admin": True})
        assert serializer.is_valid()

        # is_admin should not be in validated_data since it's read-only
        assert "is_admin" not in serializer.validated_data

    def test_update_allowed_fields(self, user):
        """Test updating allowed fields."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "9876543210",
        }
        serializer = UserDetailsSerializer(user, data=data, partial=True)

        assert serializer.is_valid()
        updated_user = serializer.save()

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.phone_number == "9876543210"


@pytest.mark.django_db
class TestUserCreateSerializer:
    """Test cases for UserCreateSerializer."""

    def test_create_user_with_valid_data(self):
        """Test creating user with valid data."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": User.Role.CONTRACTOR,
            "phone_number": "1234567890",
        }
        serializer = UserCreateSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.role == User.Role.CONTRACTOR
        assert user.phone_number == "1234567890"
        assert user.check_password("newpass123")

    def test_create_user_with_default_role(self):
        """Test creating user with default role."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        serializer = UserCreateSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.role == User.Role.CONTRACTOR

    def test_create_admin_user(self):
        """Test creating admin user."""
        data = {
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "adminpass123",
            "first_name": "Admin",
            "last_name": "User",
            "role": User.Role.ADMIN,
        }
        serializer = UserCreateSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.role == User.Role.ADMIN
        assert user.is_admin is True

    def test_validate_duplicate_email(self, user):
        """Test validation fails for duplicate email."""
        data = {
            "username": "newuser",
            "email": user.email,  # Duplicate email
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        serializer = UserCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors
        assert "already exists" in str(serializer.errors["email"][0])

    def test_validate_invalid_phone_number(self):
        """Test validation fails for invalid phone number."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "invalid-phone",
        }
        serializer = UserCreateSerializer(data=data)

        assert not serializer.is_valid()
        assert "phone_number" in serializer.errors

    def test_validate_valid_phone_number_formats(self):
        """Test validation passes for valid phone number formats."""
        valid_phones = ["+1234567890", "123-456-7890", "123 456 7890", "1234567890"]

        for phone in valid_phones:
            data = {
                "username": f"user{phone[-4:]}",
                "email": f"user{phone[-4:]}@example.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "User",
                "phone_number": phone,
            }
            serializer = UserCreateSerializer(data=data)

            assert serializer.is_valid(), f"Phone {phone} should be valid"

    def test_create_user_without_optional_fields(self):
        """Test creating user without optional fields."""
        data = {
            "username": "minimaluser",
            "email": "minimal@example.com",
            "password": "minimalpass123",
        }
        serializer = UserCreateSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.first_name == ""
        assert user.last_name == ""
        assert user.phone_number == ""
        assert user.role == User.Role.CONTRACTOR


@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test cases for UserProfileSerializer."""

    def test_serialize_user_profile(self, user):
        """Test serializing user profile."""
        profile = UserProfileService.get_or_create_profile(user)
        profile.bio = "Test bio"
        profile.two_factor_enabled = True
        profile.two_factor_method = UserProfile.TwoFactorMethod.EMAIL
        profile.save()

        serializer = UserProfileSerializer(profile)
        data = serializer.data

        assert data["id"] == profile.id
        assert data["bio"] == "Test bio"
        assert data["two_factor_enabled"] is True
        assert data["two_factor_method"] == UserProfile.TwoFactorMethod.EMAIL
        assert (
            data["two_factor_method_display"] == profile.get_two_factor_method_display()
        )

    def test_update_profile_bio(self, user):
        """Test updating profile bio."""
        profile = UserProfileService.get_or_create_profile(user)

        data = {"bio": "Updated bio"}
        serializer = UserProfileSerializer(profile, data=data, partial=True)

        assert serializer.is_valid()
        updated_profile = serializer.save()

        assert updated_profile.bio == "Updated bio"

    def test_read_only_fields(self, user):
        """Test that read-only fields cannot be updated."""
        profile = UserProfileService.get_or_create_profile(user)

        data = {"two_factor_method_display": "Should not update"}
        serializer = UserProfileSerializer(profile, data=data, partial=True)

        assert serializer.is_valid()
        # two_factor_method_display should not be in validated_data
        assert "two_factor_method_display" not in serializer.validated_data


@pytest.mark.django_db
class TestUserWithProfileSerializer:
    """Test cases for UserWithProfileSerializer."""

    def test_serialize_user_with_profile(self, user):
        """Test serializing user with profile."""
        profile = UserProfileService.get_or_create_profile(user)
        profile.bio = "Test bio"
        profile.save()

        # Refresh user to ensure profile relationship is loaded
        user.refresh_from_db()

        serializer = UserWithProfileSerializer(user)
        data = serializer.data

        assert "profile" in data
        assert data["profile"]["bio"] == "Test bio"
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name


@pytest.mark.django_db
class TestTwoFactorVerifySerializer:
    """Test cases for TwoFactorVerifySerializer."""

    def test_valid_code(self):
        """Test validation passes for valid code."""
        data = {"code": "123456"}
        serializer = TwoFactorVerifySerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["code"] == "123456"

    def test_invalid_code_length(self):
        """Test validation fails for invalid code length."""
        invalid_codes = ["12345", "1234567", ""]

        for code in invalid_codes:
            data = {"code": code}
            serializer = TwoFactorVerifySerializer(data=data)

            assert not serializer.is_valid()
            assert "code" in serializer.errors

    def test_non_digit_code(self):
        """Test validation fails for non-digit code."""
        data = {"code": "abc123"}
        serializer = TwoFactorVerifySerializer(data=data)

        assert not serializer.is_valid()
        assert "code" in serializer.errors
        assert "only digits" in str(serializer.errors["code"][0])


@pytest.mark.django_db
class TestTwoFactorSetupSerializer:
    """Test cases for TwoFactorSetupSerializer."""

    def test_enable_2fa_with_email_method(self, user, request_factory):
        """Test enabling 2FA with email method."""
        request = request_factory.post("/")
        request.user = user

        data = {"enable": True, "method": UserProfile.TwoFactorMethod.EMAIL}
        serializer = TwoFactorSetupSerializer(data=data, context={"request": request})

        assert serializer.is_valid()
        assert serializer.validated_data["enable"] is True
        assert serializer.validated_data["method"] == UserProfile.TwoFactorMethod.EMAIL

    def test_enable_2fa_with_sms_method_valid_phone(self, user, request_factory):
        """Test enabling 2FA with SMS method when user has phone number."""
        request = request_factory.post("/")
        request.user = user

        data = {"enable": True, "method": UserProfile.TwoFactorMethod.SMS}
        serializer = TwoFactorSetupSerializer(data=data, context={"request": request})

        assert serializer.is_valid()

    def test_enable_2fa_with_sms_method_no_phone(self, request_factory):
        """Test enabling 2FA with SMS method when user has no phone number."""
        user_no_phone = UserService.create_user(
            email="nophone@example.com",
            password="testpass123",
            first_name="No",
            last_name="Phone",
        )

        request = request_factory.post("/")
        request.user = user_no_phone

        data = {"enable": True, "method": UserProfile.TwoFactorMethod.SMS}
        serializer = TwoFactorSetupSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "method" in serializer.errors
        assert "Phone number is required" in str(serializer.errors["method"][0])

    def test_enable_2fa_without_method(self, user, request_factory):
        """Test enabling 2FA without specifying method."""
        request = request_factory.post("/")
        request.user = user

        data = {"enable": True}
        serializer = TwoFactorSetupSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "method" in serializer.errors
        assert "required when enabling" in str(serializer.errors["method"][0])

    def test_disable_2fa(self, user, request_factory):
        """Test disabling 2FA."""
        request = request_factory.post("/")
        request.user = user

        data = {"enable": False}
        serializer = TwoFactorSetupSerializer(data=data, context={"request": request})

        assert serializer.is_valid()
        assert serializer.validated_data["enable"] is False


@pytest.mark.django_db
class TestTwoFactorMethodSerializer:
    """Test cases for TwoFactorMethodSerializer."""

    def test_change_to_email_method(self, user, request_factory):
        """Test changing 2FA method to email."""
        request = request_factory.post("/")
        request.user = user

        data = {"method": UserProfile.TwoFactorMethod.EMAIL}
        serializer = TwoFactorMethodSerializer(data=data, context={"request": request})

        assert serializer.is_valid()
        assert serializer.validated_data["method"] == UserProfile.TwoFactorMethod.EMAIL

    def test_change_to_sms_method_with_phone(self, user, request_factory):
        """Test changing 2FA method to SMS when user has phone."""
        request = request_factory.post("/")
        request.user = user

        data = {"method": UserProfile.TwoFactorMethod.SMS}
        serializer = TwoFactorMethodSerializer(data=data, context={"request": request})

        assert serializer.is_valid()

    def test_change_to_sms_method_without_phone(self, request_factory):
        """Test changing 2FA method to SMS when user has no phone."""
        user_no_phone = UserService.create_user(
            email="nophone@example.com",
            password="testpass123",
            first_name="No",
            last_name="Phone",
        )

        request = request_factory.post("/")
        request.user = user_no_phone

        data = {"method": "sms"}
        serializer = TwoFactorMethodSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "method" in serializer.errors
        assert "Phone number is required" in str(serializer.errors["method"][0])


@pytest.mark.django_db
class TestTwoFactorStatusSerializer:
    """Test cases for TwoFactorStatusSerializer."""

    def test_serialize_2fa_status(self):
        """Test serializing 2FA status."""
        data = {
            "two_factor_enabled": True,
            "two_factor_method": UserProfile.TwoFactorMethod.EMAIL,
            "two_factor_method_display": "Email",
            "can_use_sms": False,
            "phone_number_required": True,
        }

        serializer = TwoFactorStatusSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["two_factor_enabled"] is True
        assert serialized_data["two_factor_method"] == UserProfile.TwoFactorMethod.EMAIL
        assert serialized_data["two_factor_method_display"] == "Email"
        assert serialized_data["can_use_sms"] is False
        assert serialized_data["phone_number_required"] is True


@pytest.mark.django_db
class TestPasswordChangeSerializer:
    """Test cases for PasswordChangeSerializer."""

    def test_valid_password_change(self, user, request_factory):
        """Test valid password change."""
        request = request_factory.post("/")
        request.user = user

        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        serializer = PasswordChangeSerializer(data=data, context={"request": request})

        assert serializer.is_valid()
        updated_user = serializer.save()

        assert updated_user.check_password("newpass123")
        assert not updated_user.check_password("testpass123")

    def test_incorrect_current_password(self, user, request_factory):
        """Test password change with incorrect current password."""
        request = request_factory.post("/")
        request.user = user

        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        serializer = PasswordChangeSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "old_password" in serializer.errors
        assert "incorrect" in str(serializer.errors["old_password"][0])

    def test_password_confirmation_mismatch(self, user, request_factory):
        """Test password change with mismatched confirmation."""
        request = request_factory.post("/")
        request.user = user

        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "confirm_password": "differentpass",
        }
        serializer = PasswordChangeSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "confirm_password" in serializer.errors
        assert "do not match" in str(serializer.errors["confirm_password"][0])

    @patch("users.serializers.validate_password")
    def test_weak_password_validation(self, mock_validate, user, request_factory):
        """Test password change with weak password."""
        mock_validate.side_effect = DjangoValidationError(["Password is too weak"])

        request = request_factory.post("/")
        request.user = user

        data = {
            "old_password": "testpass123",
            "new_password": "weak",
            "confirm_password": "weak",
        }
        serializer = PasswordChangeSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "new_password" in serializer.errors
        assert "Password is too weak" in str(serializer.errors["new_password"][0])

    def test_missing_required_fields(self, user, request_factory):
        """Test password change with missing required fields."""
        request = request_factory.post("/")
        request.user = user

        data = {"old_password": "testpass123"}
        serializer = PasswordChangeSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "new_password" in serializer.errors
        assert "confirm_password" in serializer.errors
