from unittest.mock import patch, MagicMock

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.test import APIRequestFactory
from rest_framework import serializers

from users.serializers import (
    TwoFactorCodeInputSerializer,
    SmartLoginInputSerializer,
    SmartLoginVerifyInputSerializer,
    UserStatsOutputSerializer,
    TwoFactorSetupOutputSerializer,
    TwoFactorStatusOutputSerializer,
    TwoFactorVerifyOutputSerializer,
    SmartLoginOutputSerializer,
    SmartLoginVerifyOutputSerializer,
    MessageOutputSerializer,
    ErrorOutputSerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


@pytest.fixture
def user():
    """Fixture for a test user."""
    return User.objects.create_user(
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
    return User.objects.create_user(
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
class TestTwoFactorCodeInputSerializer:
    """Test cases for TwoFactorCodeInputSerializer."""

    def test_valid_code(self):
        """Test validation passes for valid code."""
        data = {"code": "123456"}
        serializer = TwoFactorCodeInputSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["code"] == "123456"

    def test_missing_code(self):
        """Test validation fails for missing code."""
        data = {}
        serializer = TwoFactorCodeInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "code" in serializer.errors

    def test_empty_code(self):
        """Test validation fails for empty code."""
        data = {"code": ""}
        serializer = TwoFactorCodeInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "code" in serializer.errors

    def test_code_too_long(self):
        """Test validation fails for code that's too long."""
        data = {"code": "12345678901"}  # 11 characters, max is 10
        serializer = TwoFactorCodeInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "code" in serializer.errors


@pytest.mark.django_db
class TestSmartLoginInputSerializer:
    """Test cases for SmartLoginInputSerializer."""

    def test_valid_data(self):
        """Test validation passes for valid email and password."""
        data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        serializer = SmartLoginInputSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["email"] == "test@example.com"
        assert serializer.validated_data["password"] == "testpass123"

    def test_missing_email(self):
        """Test validation fails for missing email."""
        data = {"password": "testpass123"}
        serializer = SmartLoginInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_missing_password(self):
        """Test validation fails for missing password."""
        data = {"email": "test@example.com"}
        serializer = SmartLoginInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "password" in serializer.errors

    def test_invalid_email_format(self):
        """Test validation fails for invalid email format."""
        data = {
            "email": "invalid-email",
            "password": "testpass123"
        }
        serializer = SmartLoginInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestSmartLoginVerifyInputSerializer:
    """Test cases for SmartLoginVerifyInputSerializer."""

    def test_valid_data_with_code(self):
        """Test validation passes for valid data with code."""
        data = {
            "temp_session_id": "session123",
            "code": "1234",
            "skip": False
        }
        serializer = SmartLoginVerifyInputSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["temp_session_id"] == "session123"
        assert serializer.validated_data["code"] == "1234"
        assert serializer.validated_data["skip"] is False

    def test_valid_data_with_skip(self):
        """Test validation passes for valid data with skip."""
        data = {
            "temp_session_id": "session123",
            "skip": True
        }
        serializer = SmartLoginVerifyInputSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["temp_session_id"] == "session123"
        assert serializer.validated_data["code"] == ""  # Default value
        assert serializer.validated_data["skip"] is True

    def test_missing_temp_session_id(self):
        """Test validation fails for missing temp_session_id."""
        data = {"code": "1234"}
        serializer = SmartLoginVerifyInputSerializer(data=data)

        assert not serializer.is_valid()
        assert "temp_session_id" in serializer.errors

    def test_defaults(self):
        """Test default values are applied correctly."""
        data = {"temp_session_id": "session123"}
        serializer = SmartLoginVerifyInputSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data["code"] == ""
        assert serializer.validated_data["skip"] is False


@pytest.mark.django_db
class TestUserCreateSerializer:
    """Test cases for UserCreateSerializer."""

    def test_create_user_with_valid_data(self):
        """Test creating user with valid data."""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "re_password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": User.Role.CONTRACTOR,
            "phone_number": "1234567890",
        }
        serializer = UserCreateSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.email == "newuser@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.role == User.Role.CONTRACTOR
        assert user.phone_number == "1234567890"
        assert user.check_password("newpass123")

    def test_create_user_with_default_role(self):
        """Test creating user with default role."""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "re_password": "newpass123",
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
            "email": "admin@example.com",
            "password": "adminpass123",
            "re_password": "adminpass123",
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
            "email": user.email,  # Duplicate email
            "password": "newpass123",
            "re_password": "newpass123",
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
            "email": "newuser@example.com",
            "password": "newpass123",
            "re_password": "newpass123",
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
                "email": f"user{phone[-4:]}@example.com",
                "password": "newpass123",
                "re_password": "newpass123",
                "first_name": "New",
                "last_name": "User",
                "phone_number": phone,
            }
            serializer = UserCreateSerializer(data=data)

            assert serializer.is_valid(), f"Phone {phone} should be valid"

    def test_create_user_without_optional_fields(self):
        """Test creating user without optional fields."""
        data = {
            "email": "minimal@example.com",
            "password": "minimalpass123",
            "re_password": "minimalpass123",
        }
        serializer = UserCreateSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.first_name == ""
        assert user.last_name == ""
        assert user.phone_number == ""
        assert user.role == User.Role.CONTRACTOR


@pytest.mark.django_db
class TestUserSerializer:
    """Test cases for UserSerializer."""

    def test_serialize_user_details(self, user):
        """Test serializing user details."""
        serializer = UserSerializer(user)
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
        assert data["two_factor_enabled"] == user.two_factor_enabled

    def test_admin_user_properties(self, admin_user):
        """Test admin user properties in serialization."""
        serializer = UserSerializer(admin_user)
        data = serializer.data

        assert data["is_admin"] is True
        assert data["is_contractor"] is False
        assert data["role"] == User.Role.ADMIN

    def test_contractor_user_properties(self, user):
        """Test contractor user properties in serialization."""
        serializer = UserSerializer(user)
        data = serializer.data

        assert data["is_admin"] is False
        assert data["is_contractor"] is True
        assert data["role"] == User.Role.CONTRACTOR

    def test_read_only_fields(self, user):
        """Test that read-only fields cannot be updated."""
        serializer = UserSerializer(user, data={"role": User.Role.ADMIN}, partial=True)
        assert serializer.is_valid()

        # role should be in validated_data since it's not read-only in UserSerializer
        assert "role" in serializer.validated_data

    def test_update_allowed_fields(self, user):
        """Test updating allowed fields."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "9876543210",
        }
        serializer = UserSerializer(user, data=data, partial=True)

        assert serializer.is_valid()
        updated_user = serializer.save()

        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.phone_number == "9876543210"


@pytest.mark.django_db
class TestOutputSerializers:
    """Test cases for output serializers."""

    def test_user_stats_output_serializer(self):
        """Test UserStatsOutputSerializer."""
        data = {
            "total_users": 10,
            "admin_users": 2,
            "contractor_users": 8,
            "active_users": 9,
            "inactive_users": 1,
        }
        serializer = UserStatsOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["total_users"] == 10
        assert serialized_data["admin_users"] == 2
        assert serialized_data["contractor_users"] == 8
        assert serialized_data["active_users"] == 9
        assert serialized_data["inactive_users"] == 1

    def test_two_factor_setup_output_serializer(self):
        """Test TwoFactorSetupOutputSerializer."""
        data = {
            "qr_code": "data:image/png;base64,test",
            "secret_key": "JBSWY3DPEHPK3PXP",
            "backup_codes": ["123456", "789012"],
            "instructions": "Scan the QR code",
        }
        serializer = TwoFactorSetupOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["qr_code"] == "data:image/png;base64,test"
        assert serialized_data["secret_key"] == "JBSWY3DPEHPK3PXP"
        assert serialized_data["backup_codes"] == ["123456", "789012"]
        assert serialized_data["instructions"] == "Scan the QR code"

    def test_two_factor_status_output_serializer(self):
        """Test TwoFactorStatusOutputSerializer."""
        data = {
            "enabled": True,
            "message": "Two-factor authentication is enabled",
        }
        serializer = TwoFactorStatusOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["enabled"] is True
        assert serialized_data["message"] == "Two-factor authentication is enabled"

    def test_two_factor_verify_output_serializer(self):
        """Test TwoFactorVerifyOutputSerializer."""
        data = {
            "valid": True,
            "message": "Code verified successfully",
        }
        serializer = TwoFactorVerifyOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["valid"] is True
        assert serialized_data["message"] == "Code verified successfully"

    def test_smart_login_output_serializer(self):
        """Test SmartLoginOutputSerializer."""
        data = {
            "requires_2fa": True,
            "temp_session_id": "session123",
            "delivery_method": "email",
            "masked_email": "t***@example.com",
            "message": "Please complete 2FA verification",
        }
        serializer = SmartLoginOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["requires_2fa"] is True
        assert serialized_data["temp_session_id"] == "session123"
        assert serialized_data["delivery_method"] == "email"
        assert serialized_data["masked_email"] == "t***@example.com"
        assert serialized_data["message"] == "Please complete 2FA verification"

    def test_smart_login_verify_output_serializer(self):
        """Test SmartLoginVerifyOutputSerializer."""
        data = {
            "access": "access_token_123",
            "refresh": "refresh_token_123",
            "user": {
                "id": 1,
                "email": "test@example.com",
                "first_name": "Test",
                "last_name": "User",
            },
            "message": "Login successful",
        }
        serializer = SmartLoginVerifyOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["access"] == "access_token_123"
        assert serialized_data["refresh"] == "refresh_token_123"
        assert serialized_data["user"]["id"] == 1
        assert serialized_data["user"]["email"] == "test@example.com"
        assert serialized_data["message"] == "Login successful"

    def test_message_output_serializer(self):
        """Test MessageOutputSerializer."""
        data = {"message": "Operation completed successfully"}
        serializer = MessageOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["message"] == "Operation completed successfully"

    def test_error_output_serializer(self):
        """Test ErrorOutputSerializer."""
        data = {"error": "Something went wrong"}
        serializer = ErrorOutputSerializer(data)
        serialized_data = serializer.data

        assert serialized_data["error"] == "Something went wrong"
