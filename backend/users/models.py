from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CONTRACTOR = "contractor", "Contractor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTRACTOR,
        help_text="User role for access control",
    )

    phone_number = models.CharField(
        max_length=20, blank=True, null=True, help_text="Phone number for SMS 2FA"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_user"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN

    @property
    def is_contractor(self):
        """Check if user has contractor role."""
        return self.role == self.Role.CONTRACTOR

    def save(self, *args, **kwargs):
        """Override save to set is_staff based on role."""
        if self.role == self.Role.ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended user profile information.
    """

    class TwoFactorMethod(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # 2FA related fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=10,
        choices=TwoFactorMethod.choices,
        default=TwoFactorMethod.EMAIL,
        help_text="Preferred 2FA verification method",
    )
    backup_tokens = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users_userprofile"
        indexes = [
            models.Index(fields=["two_factor_method"]),
        ]

    def __str__(self):
        return f"Profile for {self.user.username}"


class TwoFactorCode(models.Model):
    """
    Model to track 2FA verification codes.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="two_factor_codes"
    )

    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "users_twofactorcode"
        indexes = [
            models.Index(fields=["user", "code"]),
            models.Index(fields=["expires_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"2FA Code for {self.user.username}"

    @property
    def is_expired(self):
        """Check if the code has expired."""
        from django.utils import timezone

        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if the code is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired
