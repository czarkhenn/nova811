from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, UserProfile
from .permissions import CanManageUsers, IsAdminUser
from .serializers import (
    PasswordChangeSerializer,
    TwoFactorMethodSerializer,
    TwoFactorSetupSerializer,
    TwoFactorStatusSerializer,
    TwoFactorVerifySerializer,
    UserDetailsSerializer,
    UserProfileSerializer,
)
from .services import (
    PermissionService,
    TwoFactorService,
    UserProfileService,
    UserService,
)

User = get_user_model()


class UserListAPIView(APIView):
    """
    API view to list users (admin only) or get current user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get list of users (admin) or current user info.
        """
        if PermissionService.is_admin(request.user):
            users = User.objects.all().select_related("profile")
            serializer = UserDetailsSerializer(users, many=True)
            return Response(serializer.data)
        else:
            # Non-admin users get their own info
            serializer = UserDetailsSerializer(request.user)
            return Response(serializer.data)


class UserDetailAPIView(APIView):
    """
    API view to get, update user details.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        """
        Get user object with permission check.
        """
        try:
            user = User.objects.select_related("profile").get(pk=pk)

            # Check permissions
            if (
                not PermissionService.is_admin(self.request.user)
                and user != self.request.user
            ):
                return None

            return user
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Get user details.
        """
        user = self.get_object(pk)
        if not user:
            return Response(
                {"error": "User not found or permission denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserDetailsSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Update user details.
        """
        user = self.get_object(pk)
        if not user:
            return Response(
                {"error": "User not found or permission denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserDetailsSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateAPIView(APIView):
    """
    API view to create new users (admin only).
    """

    permission_classes = [IsAuthenticated, CanManageUsers]

    def post(self, request):
        """
        Create a new user.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        role = request.data.get("role", User.Role.CONTRACTOR)
        phone_number = request.data.get("phone_number")

        if not all([email, password, first_name, last_name]):
            return Response(
                {"error": "Email, password, first_name, and last_name are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserService.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone_number=phone_number,
            )
            serializer = UserDetailsSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserRoleUpdateAPIView(APIView):
    """
    API view to update user role (admin only).
    """

    permission_classes = [IsAuthenticated, CanManageUsers]

    def post(self, request, pk):
        """
        Change user role.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        new_role = request.data.get("role")
        if not new_role:
            return Response(
                {"error": "Role is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_user = UserService.update_user_role(user, new_role)
            serializer = UserDetailsSerializer(updated_user)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserActivateAPIView(APIView):
    """
    API view to activate user (admin only).
    """

    permission_classes = [IsAuthenticated, CanManageUsers]

    def post(self, request, pk):
        """
        Activate user account.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        activated_user = UserService.activate_user(user)
        serializer = UserDetailsSerializer(activated_user)
        return Response(serializer.data)


class UserDeactivateAPIView(APIView):
    """
    API view to deactivate user (admin only).
    """

    permission_classes = [IsAuthenticated, CanManageUsers]

    def post(self, request, pk):
        """
        Deactivate user account.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        deactivated_user = UserService.deactivate_user(user)
        serializer = UserDetailsSerializer(deactivated_user)
        return Response(serializer.data)


class UserProfileAPIView(APIView):
    """
    API view for user profile management.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get current user's profile.
        """
        profile = UserProfileService.get_or_create_profile(request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        """
        Update current user's profile.
        """
        bio = request.data.get("bio")
        avatar = request.FILES.get("avatar")

        profile = UserProfileService.update_profile(
            request.user, bio=bio, avatar=avatar
        )
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)


class TwoFactorSetupAPIView(APIView):
    """
    API view for 2FA setup.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get current 2FA status with detailed information.
        """
        user = request.user
        is_enabled = TwoFactorService.is_2fa_enabled(user)
        method = TwoFactorService.get_2fa_method(user)
        can_use_sms = TwoFactorService.can_use_sms(user)

        data = {
            "two_factor_enabled": is_enabled,
            "two_factor_method": method,
            "two_factor_method_display": "Email"
            if method == UserProfile.TwoFactorMethod.EMAIL
            else "SMS",
            "can_use_sms": can_use_sms,
            "phone_number_required": not bool(
                user.phone_number and user.phone_number.strip()
            ),
        }

        serializer = TwoFactorStatusSerializer(data)
        return Response(serializer.data)

    def post(self, request):
        """
        Enable or disable 2FA for the current user with method selection.
        """
        serializer = TwoFactorSetupSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            enable = serializer.validated_data["enable"]
            method = serializer.validated_data.get(
                "method", UserProfile.TwoFactorMethod.EMAIL
            )

            if enable:
                success = TwoFactorService.enable_2fa(request.user, method)
                message = f"2FA enabled successfully with {method} verification"
            else:
                success = TwoFactorService.disable_2fa(request.user)
                message = "2FA disabled successfully"

            if success:
                return Response({"message": message})
            else:
                return Response(
                    {"error": "Failed to update 2FA settings"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorMethodAPIView(APIView):
    """
    API view for changing 2FA method.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Change user's 2FA method.
        """
        serializer = TwoFactorMethodSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            method = serializer.validated_data["method"]

            try:
                success = TwoFactorService.set_2fa_method(request.user, method)
                if success:
                    method_display = (
                        "Email"
                        if method == UserProfile.TwoFactorMethod.EMAIL
                        else "SMS"
                    )
                    return Response(
                        {
                            "message": f"2FA method changed to {method_display}",
                            "method": method,
                        }
                    )
                else:
                    return Response(
                        {"error": "Failed to update 2FA method"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorRequestCodeAPIView(APIView):
    """
    API view to request a 2FA code.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Generate and send a 2FA code to the user.
        """
        user = request.user

        # Check if 2FA is enabled
        if not TwoFactorService.is_2fa_enabled(user):
            return Response(
                {"error": "2FA is not enabled for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate and send code
        two_factor_code = TwoFactorService.create_2fa_code(user)
        TwoFactorService.send_2fa_code(user, two_factor_code.code)

        return Response(
            {
                "message": "Verification code sent successfully",
                "expires_at": two_factor_code.expires_at,
            }
        )


class TwoFactorVerifyAPIView(APIView):
    """
    API view to verify 2FA code.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Verify the 2FA code.
        """
        serializer = TwoFactorVerifySerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            user = request.user

            # Verify the code
            is_valid = TwoFactorService.verify_2fa_code(user, code)

            if is_valid:
                return Response(
                    {"message": "Code verified successfully", "verified": True}
                )
            else:
                return Response(
                    {"error": "Invalid or expired code", "verified": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    """
    API view for password change.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Change user password.
        """
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminStatsAPIView(APIView):
    """
    API view for admin statistics.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """
        Get admin dashboard statistics.
        """
        total_users = User.objects.count()
        admin_users = User.objects.filter(role=User.Role.ADMIN).count()
        contractor_users = User.objects.filter(role=User.Role.CONTRACTOR).count()
        active_users = User.objects.filter(is_active=True).count()
        users_with_2fa = UserProfile.objects.filter(two_factor_enabled=True).count()

        return Response(
            {
                "total_users": total_users,
                "admin_users": admin_users,
                "contractor_users": contractor_users,
                "active_users": active_users,
                "users_with_2fa": users_with_2fa,
            }
        )
