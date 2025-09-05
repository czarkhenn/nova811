from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

User = get_user_model()


class UserDetailsSerializer(BaseUserSerializer):
    """
    Output serializer for user details.
    Used for displaying user information in API responses.
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
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "username",
            "date_joined",
            "created_at",
            "updated_at",
            "is_admin",
            "is_contractor",
            "role_display",
            "is_active",
        )


class UserCreateSerializer(BaseUserCreateSerializer):
    """
    Input serializer for user registration.
    Handles user creation with custom fields and validation.
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
        help_text="Phone number for potential SMS 2FA",
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "role",
            "phone_number",
        )

    def validate_email(self, value):
        """
        Validate email uniqueness.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """
        Validate phone number format if provided.
        """
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
        Create user with custom fields.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data.get("role", User.Role.CONTRACTOR),
            phone_number=validated_data.get("phone_number", ""),
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Output serializer for user profile information.
    """

    two_factor_method_display = serializers.CharField(
        source="get_two_factor_method_display", read_only=True
    )

    class Meta:
        from users.models import UserProfile

        model = UserProfile
        fields = (
            "id",
            "bio",
            "avatar",
            "two_factor_enabled",
            "two_factor_method",
            "two_factor_method_display",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "two_factor_method_display",
        )


class UserWithProfileSerializer(UserDetailsSerializer):
    """
    Output serializer for user with profile information.
    """

    profile = UserProfileSerializer(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ("profile",)


class TwoFactorVerifySerializer(serializers.Serializer):
    """
    Input serializer for verifying 2FA codes.
    """

    code = serializers.CharField(
        max_length=6, min_length=6, help_text="6-digit verification code"
    )

    def validate_code(self, value):
        """
        Validate that code contains only digits.
        """
        if not value.isdigit():
            raise serializers.ValidationError("Code must contain only digits.")
        return value


class TwoFactorSetupSerializer(serializers.Serializer):
    """
    Input serializer for enabling/disabling 2FA.
    """

    enable = serializers.BooleanField(help_text="Enable or disable 2FA")
    method = serializers.ChoiceField(
        choices=[],  # Will be set in __init__
        required=False,
        help_text="2FA method (required when enabling)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from users.models import UserProfile

        self.fields["method"].choices = UserProfile.TwoFactorMethod.choices

    def validate(self, attrs):
        """
        Validate 2FA setup data.
        """
        enable = attrs.get("enable")
        method = attrs.get("method")
        request = self.context.get("request")

        if enable and not method:
            raise serializers.ValidationError(
                {"method": "Method is required when enabling 2FA."}
            )

        if enable and method:
            from users.models import UserProfile

            if method == UserProfile.TwoFactorMethod.SMS:
                if not request or not request.user.phone_number:
                    raise serializers.ValidationError(
                        {"method": "Phone number is required for SMS 2FA."}
                    )

        return attrs


class TwoFactorMethodSerializer(serializers.Serializer):
    """
    Input serializer for changing 2FA method.
    """

    method = serializers.ChoiceField(
        choices=[],  # Will be set in __init__
        help_text="New 2FA method",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from users.models import UserProfile

        self.fields["method"].choices = UserProfile.TwoFactorMethod.choices

    def validate_method(self, value):
        """
        Validate 2FA method availability.
        """
        request = self.context.get("request")

        if value == "sms" and request:
            if not request.user.phone_number:
                raise serializers.ValidationError(
                    "Phone number is required for SMS 2FA."
                )

        return value


class TwoFactorStatusSerializer(serializers.Serializer):
    """
    Output serializer for 2FA status information.
    """

    two_factor_enabled = serializers.BooleanField(
        read_only=True, help_text="Whether 2FA is enabled"
    )
    two_factor_method = serializers.CharField(
        read_only=True, help_text="Current 2FA method"
    )
    two_factor_method_display = serializers.CharField(
        read_only=True, help_text="Human-readable 2FA method"
    )
    can_use_sms = serializers.BooleanField(
        read_only=True, help_text="Whether SMS 2FA is available"
    )
    phone_number_required = serializers.BooleanField(
        read_only=True, help_text="Whether phone number is required for SMS"
    )


class PasswordChangeSerializer(serializers.Serializer):
    """
    Input serializer for password change.
    """

    old_password = serializers.CharField(write_only=True, help_text="Current password")
    new_password = serializers.CharField(write_only=True, help_text="New password")
    confirm_password = serializers.CharField(
        write_only=True, help_text="Confirm new password"
    )

    def validate_old_password(self, value):
        """
        Validate current password.
        """
        request = self.context.get("request")
        if request and not request.user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """
        Validate new password using Django's password validators.
        """
        request = self.context.get("request")
        if request:
            try:
                validate_password(value, request.user)
            except DjangoValidationError as e:
                raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match."}
            )

        return attrs

    def save(self):
        """
        Save the new password.
        """
        request = self.context.get("request")
        if request:
            request.user.set_password(self.validated_data["new_password"])
            request.user.save()
            return request.user
