import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import TwoFactorCode, User, UserProfile


class UserService:
    """
    Service for user management operations.
    """

    @staticmethod
    def create_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = User.Role.CONTRACTOR,
        phone_number: str = None,
    ) -> User:
        """
        Create a new user with profile.
        """
        with transaction.atomic():
            user = User.objects.create_user(
                email=email,
                username=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone_number=phone_number or "",
            )

            # Create user profile
            UserProfile.objects.create(user=user)

            return user

    @staticmethod
    def update_user_role(user: User, role: str) -> User:
        """
        Update user role and related permissions.
        """
        if role not in [User.Role.ADMIN, User.Role.CONTRACTOR]:
            raise ValidationError(f"Invalid role: {role}")

        user.role = role
        user.save()
        return user

    @staticmethod
    def get_users_by_role(role: str):
        """
        Get all users with specific role.
        """
        return User.objects.filter(role=role).select_related("profile")

    @staticmethod
    def activate_user(user: User) -> User:
        """
        Activate a user account.
        """
        user.is_active = True
        user.save()
        return user

    @staticmethod
    def deactivate_user(user: User) -> User:
        """
        Deactivate a user account.
        """
        user.is_active = False
        user.save()
        return user


class AuthenticationService:
    """
    Service for authentication operations.
    """

    @staticmethod
    def authenticate_user(email: str, password: str) -> User:
        """
        Authenticate user with email and password.
        """
        user = authenticate(username=email, password=password)
        if not user:
            raise ValidationError("Invalid credentials")

        if not user.is_active:
            raise ValidationError("User account is disabled")

        return user

    @staticmethod
    def check_login_attempts(email: str) -> bool:
        """
        Check if user has exceeded login attempts.
        """

        return True

    @staticmethod
    def reset_login_attempts(email: str):
        """
        Reset failed login attempts for user.
        """
        # TODO: Implement login attempt tracking
        pass


class TwoFactorService:
    """
    Service for 2FA operations supporting both email and SMS.
    """

    @staticmethod
    def generate_2fa_code() -> str:
        """
        Generate a 6-digit 2FA code.
        For local development, always return '123456'.
        """
        if settings.DEBUG:
            return "123456"

        return "".join(secrets.choice(string.digits) for _ in range(6))

    @staticmethod
    def create_2fa_code(user: User) -> TwoFactorCode:
        """
        Create a new 2FA code for user.
        """
        # Invalidate any existing unused codes
        TwoFactorCode.objects.filter(user=user, is_used=False).update(is_used=True)

        code = TwoFactorService.generate_2fa_code()
        expires_at = timezone.now() + timedelta(minutes=10)

        two_factor_code = TwoFactorCode.objects.create(
            user=user, code=code, expires_at=expires_at
        )

        return two_factor_code

    @staticmethod
    def verify_2fa_code(user: User, code: str) -> bool:
        """
        Verify 2FA code for user.
        """
        try:
            two_factor_code = TwoFactorCode.objects.get(
                user=user, code=code, is_used=False
            )

            if two_factor_code.is_expired:
                return False

            # Mark code as used
            two_factor_code.is_used = True
            two_factor_code.save()

            return True

        except TwoFactorCode.DoesNotExist:
            return False

    @staticmethod
    def enable_2fa(user: User, method: str = UserProfile.TwoFactorMethod.EMAIL) -> bool:
        """
        Enable 2FA for user with specified method.
        """
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.two_factor_enabled = True
        profile.two_factor_method = method
        profile.save()
        return True

    @staticmethod
    def disable_2fa(user: User) -> bool:
        """
        Disable 2FA for user.
        """
        try:
            profile = user.profile
            profile.two_factor_enabled = False
            profile.save()

            # Invalidate any existing codes
            TwoFactorCode.objects.filter(user=user, is_used=False).update(is_used=True)

            return True
        except UserProfile.DoesNotExist:
            return False

    @staticmethod
    def is_2fa_enabled(user: User) -> bool:
        """
        Check if 2FA is enabled for user.
        """
        try:
            # Fetch profile directly from database to ensure we get the latest data
            profile = UserProfile.objects.get(user=user)
            return profile.two_factor_enabled
        except UserProfile.DoesNotExist:
            return False

    @staticmethod
    def get_2fa_method(user: User) -> str:
        """
        Get user's preferred 2FA method.
        """
        try:
            return user.profile.two_factor_method
        except UserProfile.DoesNotExist:
            return UserProfile.TwoFactorMethod.EMAIL

    @staticmethod
    def set_2fa_method(user: User, method: str) -> bool:
        """
        Set user's preferred 2FA method.
        """
        if method not in [
            UserProfile.TwoFactorMethod.EMAIL,
            UserProfile.TwoFactorMethod.SMS,
        ]:
            raise ValidationError(f"Invalid 2FA method: {method}")

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.two_factor_method = method
        profile.save()
        return True

    @staticmethod
    def send_2fa_code(user: User, code: str, method: str = None):
        """
        Send 2FA code to user via their preferred method.
        For local development, just print to console.
        """
        if method is None:
            method = TwoFactorService.get_2fa_method(user)

        if settings.DEBUG:
            print(f"2FA Code for {user.email}: {code}")
            return

        # Send via appropriate method
        if method == UserProfile.TwoFactorMethod.EMAIL:
            TwoFactorService._send_email_code(user, code)
        elif method == UserProfile.TwoFactorMethod.SMS:
            TwoFactorService._send_sms_code(user, code)

    @staticmethod
    def _send_email_code(user: User, code: str):
        """
        Send 2FA code via email.
        """
        from django.core.mail import send_mail

        subject = "Your 2FA Verification Code"
        message = (
            f"Your verification code is: {code}\n\nThis code will expire in 10 minutes."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def _send_sms_code(user: User, code: str):
        """
        Send 2FA code via SMS.
        In production, integrate with SMS service like Twilio.
        """
        if not user.phone_number:
            raise ValidationError("User has no phone number for SMS verification")

        # For now, this is a placeholder
        message = f"Your Nova811 verification code is: {code}. Valid for 10 minutes."

        # Example integration with SMS service:
        # sms_service.send_message(
        #     to=user.phone_number,
        #     message=message
        # )

        # For development, we already print to console in send_2fa_code
        pass

    @staticmethod
    def can_use_sms(user: User) -> bool:
        """
        Check if user can use SMS 2FA (has phone number).
        """
        return bool(user.phone_number and user.phone_number.strip())


class UserProfileService:
    """
    Service for user profile operations.
    """

    @staticmethod
    def get_or_create_profile(user: User) -> UserProfile:
        """
        Get or create user profile.
        """
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def update_profile(user: User, bio: str = None, avatar=None) -> UserProfile:
        """
        Update user profile information.
        """
        profile = UserProfileService.get_or_create_profile(user)

        if bio is not None:
            profile.bio = bio

        if avatar is not None:
            profile.avatar = avatar

        profile.save()
        return profile

    @staticmethod
    def delete_avatar(user: User) -> UserProfile:
        """
        Delete user avatar.
        """
        profile = UserProfileService.get_or_create_profile(user)
        if profile.avatar:
            profile.avatar.delete()
        profile.save()
        return profile


class PermissionService:
    """
    Service for role-based permission checks.
    """

    @staticmethod
    def is_admin(user: User) -> bool:
        """
        Check if user has admin role.
        """
        return user.is_authenticated and user.role == User.Role.ADMIN

    @staticmethod
    def is_contractor(user: User) -> bool:
        """
        Check if user has contractor role.
        """
        return user.is_authenticated and user.role == User.Role.CONTRACTOR

    @staticmethod
    def can_manage_users(user: User) -> bool:
        """
        Check if user can manage other users.
        """
        return PermissionService.is_admin(user)

    @staticmethod
    def can_access_admin_features(user: User) -> bool:
        """
        Check if user can access admin features.
        """
        return PermissionService.is_admin(user)

    @staticmethod
    def can_create_tickets(user: User) -> bool:
        """
        Check if user can create tickets.
        """
        return user.is_authenticated  # Both roles can create tickets

    @staticmethod
    def can_manage_tickets(user: User) -> bool:
        """
        Check if user can manage all tickets.
        """
        return PermissionService.is_admin(user)
