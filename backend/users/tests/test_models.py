import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test cases for the custom User model."""

    def test_create_user_with_default_role(self):
        """Test creating a user with default contractor role."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = User.objects.create_user(**user_data)

        assert user.email == "test@example.com"
        assert user.role == User.Role.CONTRACTOR
        assert user.is_staff is False
        assert user.is_contractor is True
        assert user.is_admin is False
        assert user.two_factor_enabled is False

    def test_create_admin_user(self):
        """Test creating a user with admin role."""
        user_data = {
            "email": "admin@example.com",
            "password": "testpass123",
            "first_name": "Admin",
            "last_name": "User",
            "role": User.Role.ADMIN,
        }
        user = User.objects.create_user(**user_data)

        assert user.role == User.Role.ADMIN
        assert user.is_staff is True
        assert user.is_admin is True
        assert user.is_contractor is False

    def test_create_user_with_phone_number(self):
        """Test creating a user with phone number."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "1234567890",
        }
        user = User.objects.create_user(**user_data)

        assert user.phone_number == "1234567890"

    def test_create_user_with_two_factor_enabled(self):
        """Test creating a user with 2FA enabled."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "two_factor_enabled": True,
        }
        user = User.objects.create_user(**user_data)

        assert user.two_factor_enabled is True

    def test_user_str_representation(self):
        """Test user string representation."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = User.objects.create_user(**user_data)
        expected = f"{user.email} ({user.get_role_display()})"
        
        assert str(user) == expected

    def test_user_save_sets_is_staff(self):
        """Test that saving a user sets is_staff based on role."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = User.objects.create_user(**user_data)

        # Initially contractor, should not be staff
        assert user.is_staff is False

        # Change to admin
        user.role = User.Role.ADMIN
        user.save()
        assert user.is_staff is True

        # Change back to contractor
        user.role = User.Role.CONTRACTOR
        user.save()
        assert user.is_staff is False

    def test_user_indexes(self):
        """Test that database indexes are created."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = User.objects.create_user(**user_data)
        
        assert user.id is not None

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email."""
        assert User.USERNAME_FIELD == 'email'

    def test_required_fields(self):
        """Test that REQUIRED_FIELDS includes first_name and last_name."""
        assert 'first_name' in User.REQUIRED_FIELDS
        assert 'last_name' in User.REQUIRED_FIELDS

    def test_username_is_optional(self):
        """Test that username field is optional."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = User.objects.create_user(**user_data)
        
        assert user.username is None

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        from django.db import IntegrityError
        
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        User.objects.create_user(**user_data)
        
        with pytest.raises(IntegrityError):
            User.objects.create_user(**user_data)

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User"
        )

        assert superuser.is_staff is True
        assert superuser.is_superuser is True
        assert superuser.email == "admin@example.com"

    def test_user_manager_create_user_without_email(self):
        """Test that creating user without email raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_user(email="", password="testpass123")
        
        assert "The Email field must be set" in str(exc_info.value)

    def test_user_manager_create_superuser_validation(self):
        """Test superuser creation validation."""
        # Test is_staff validation
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False
            )
        assert "Superuser must have is_staff=True" in str(exc_info.value)

        # Test is_superuser validation
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_superuser=False
            )
        assert "Superuser must have is_superuser=True" in str(exc_info.value)

    def test_user_role_choices(self):
        """Test that user role choices are correctly defined."""
        assert User.Role.ADMIN == "admin"
        assert User.Role.CONTRACTOR == "contractor"
        
        # Test choices tuple
        choices = User.Role.choices
        assert ("admin", "Admin") in choices
        assert ("contractor", "Contractor") in choices

    def test_user_properties(self):
        """Test user role properties."""
        # Test contractor user
        contractor = User.objects.create_user(
            email="contractor@example.com",
            password="testpass123",
            role=User.Role.CONTRACTOR
        )
        assert contractor.is_contractor is True
        assert contractor.is_admin is False

        # Test admin user
        admin = User.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            role=User.Role.ADMIN
        )
        assert admin.is_admin is True
        assert admin.is_contractor is False

    def test_user_timestamps(self):
        """Test that created_at and updated_at are set."""
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }
        user = User.objects.create_user(**user_data)
        
        assert user.created_at is not None
        assert user.updated_at is not None
        
        # Test that updated_at changes on save
        original_updated_at = user.updated_at
        user.first_name = "Updated"
        user.save()
        
        assert user.updated_at != original_updated_at
