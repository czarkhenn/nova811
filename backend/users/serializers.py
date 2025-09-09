from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
import uuid
import re

User = get_user_model()


# Input Serializers for API Views
class TwoFactorCodeInputSerializer(serializers.Serializer):
    """Input serializer for 2FA code verification."""
    code = serializers.CharField(
        max_length=10,
        required=True,
        help_text="Two-factor authentication code"
    )


class SmartLoginInputSerializer(serializers.Serializer):
    """Input serializer for smart login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class SmartLoginVerifyInputSerializer(serializers.Serializer):
    """Input serializer for smart login verification."""
    temp_session_id = serializers.CharField(required=True)
    code = serializers.CharField(required=False, allow_blank=True, default='')
    skip = serializers.BooleanField(required=False, default=False)


# Output Serializers for API Views
class UserStatsOutputSerializer(serializers.Serializer):
    """Output serializer for user statistics."""
    total_users = serializers.IntegerField()
    admin_users = serializers.IntegerField()
    contractor_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()


class TwoFactorSetupOutputSerializer(serializers.Serializer):
    """Output serializer for 2FA setup data."""
    qr_code = serializers.CharField()
    secret_key = serializers.CharField()
    backup_codes = serializers.ListField(child=serializers.CharField())
    instructions = serializers.CharField()


class TwoFactorStatusOutputSerializer(serializers.Serializer):
    """Output serializer for 2FA status."""
    enabled = serializers.BooleanField()
    message = serializers.CharField()


class TwoFactorVerifyOutputSerializer(serializers.Serializer):
    """Output serializer for 2FA verification."""
    valid = serializers.BooleanField()
    message = serializers.CharField()


class SmartLoginOutputSerializer(serializers.Serializer):
    """Output serializer for smart login response."""
    requires_2fa = serializers.BooleanField()
    temp_session_id = serializers.CharField()
    delivery_method = serializers.CharField()
    masked_email = serializers.CharField()
    message = serializers.CharField()


class SmartLoginVerifyOutputSerializer(serializers.Serializer):
    """Output serializer for smart login verification response."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.DictField()  # Will be populated with user data
    message = serializers.CharField()


class MessageOutputSerializer(serializers.Serializer):
    """Generic output serializer for simple message responses."""
    message = serializers.CharField()


class ErrorOutputSerializer(serializers.Serializer):
    """Generic output serializer for error responses."""
    error = serializers.CharField()


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Custom user creation serializer for Djoser.
    Handles role field with email-based authentication.
    """

    role = serializers.ChoiceField(
        choices=User.Role.choices,
        default=User.Role.CONTRACTOR,
        help_text="User role for access control",
    )
    phone_number = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Phone number for contact",
    )
    
    re_password = serializers.CharField(
        write_only=True,
        help_text="Password confirmation"
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
            "re_password",
            "role",
            "phone_number",
        )

    def validate(self, attrs):
        """Validate that passwords match."""
        password = attrs.get('password')
        re_password = attrs.get('re_password')
        
        if password != re_password:
            raise serializers.ValidationError({"re_password": "Passwords do not match."})
        
        return attrs

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """Validate phone number format if provided."""
        if (
            value
            and not value.replace("+", "").replace("-", "").replace(" ", "").isdigit()
        ):
            raise serializers.ValidationError(
                "Phone number must contain only digits, spaces, hyphens, and plus sign."
            )
        return value

    def create(self, validated_data):
        """
        Create user using custom manager with email-based authentication.
        """
        # Extract custom fields
        role = validated_data.pop('role', User.Role.CONTRACTOR)
        phone_number = validated_data.pop('phone_number', '')
        
        # Extract required fields for create_user
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Remove re_password as it's not needed for user creation
        validated_data.pop('re_password', None)
        
        # Create user with email-based manager
        user = User.objects.create_user(
            email=email,
            password=password,
            role=role,
            phone_number=phone_number,
            **validated_data  # This includes first_name, last_name, etc.
        )
        
        return user


class UserSerializer(BaseUserSerializer):
    """
    User serializer for Djoser responses.
    """

    role_display = serializers.CharField(source="get_role_display", read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    is_contractor = serializers.BooleanField(read_only=True)

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "phone_number",
            "is_admin",
            "is_contractor",
            "is_active",
            "date_joined",
            "last_login",
            "two_factor_enabled",
        )
        read_only_fields = (
            "id",
            "username",
            "date_joined",
            "last_login",
            "is_admin",
            "is_contractor",
            "role_display",
            "two_factor_enabled",
        )
