from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
import re


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CONTRACTOR = "contractor", "Contractor"

    # Override email field to make it unique
    email = models.EmailField(
        unique=True,
        help_text="Email address for authentication"
    )

    # Make username optional and not required
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Optional username field"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTRACTOR,
        help_text="User role for access control",
    )

    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="Phone number for contact"
    )

    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is enabled for this user"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Required for createsuperuser

    # Use custom manager
    objects = UserManager()

    class Meta:
        db_table = "users_user"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN

    @property
    def is_contractor(self):
        """Check if user has contractor role."""
        return self.role == self.Role.CONTRACTOR

    def save(self, *args, **kwargs):
        """
        Override save to set is_staff based on role.
        Business rule: Admin users should be staff.
        """
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)
