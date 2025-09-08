import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .services import PermissionService, TwoFactorService, LoginService
from .selectors import UserSelector
from .serializers import (
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
    UserSerializer,
)

logger = logging.getLogger(__name__)


class UserStatsApi(APIView):
    """
    API for retrieving user statistics for admin dashboard.
    
    GET /api/users/stats/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user statistics for admin dashboard."""
        try:
            # Check permissions using service
            if not PermissionService.can_view_user_stats(request.user):
                logger.warning(f"User {request.user.id} attempted to access user stats without permission")
                return Response(
                    ErrorOutputSerializer({"error": "Permission denied"}).data,
                    status=status.HTTP_403_FORBIDDEN
                )
            
            stats = UserSelector.get_user_count_by_role()
            logger.info(f"User stats retrieved by user {request.user.id}")
            
            serializer = UserStatsOutputSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving user stats: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorSetupApi(APIView):
    """
    API for getting 2FA setup data including QR code and instructions.
    
    GET /api/users/two-factor/setup/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get 2FA setup data including QR code and instructions."""
        try:
            setup_data = TwoFactorService.get_setup_data(request.user)
            logger.info(f"2FA setup data retrieved for user {request.user.id}")
            
            serializer = TwoFactorSetupOutputSerializer(setup_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.warning(f"Validation error in 2FA setup for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in 2FA setup for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorEnableApi(APIView):
    """
    API for enabling 2FA for the authenticated user.
    
    POST /api/users/two-factor/enable/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Enable 2FA for the authenticated user."""
        serializer = TwoFactorCodeInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                ErrorOutputSerializer({"error": "Invalid input data"}).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_code = serializer.validated_data['code']
        
        # Verify the code first
        if not TwoFactorService.verify_code(verification_code):
            logger.warning(f"Invalid 2FA code attempt for user {request.user.id}")
            return Response(
                ErrorOutputSerializer({"error": "Invalid verification code"}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            TwoFactorService.enable_2fa(request.user)
            logger.info(f"2FA enabled for user {request.user.id}")
            
            response_data = {"message": "Two-factor authentication enabled successfully"}
            serializer = MessageOutputSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.warning(f"Validation error enabling 2FA for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error enabling 2FA for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorDisableApi(APIView):
    """
    API for disabling 2FA for the authenticated user.
    
    POST /api/users/two-factor/disable/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Disable 2FA for the authenticated user."""
        try:
            TwoFactorService.disable_2fa(request.user)
            logger.info(f"2FA disabled for user {request.user.id}")
            
            response_data = {"message": "Two-factor authentication disabled successfully"}
            serializer = MessageOutputSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.warning(f"Validation error disabling 2FA for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": str(e)}).data,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error disabling 2FA for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorVerifyApi(APIView):
    """
    API for verifying 2FA code for authenticated user.
    
    POST /api/users/two-factor/verify/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Verify 2FA code for authenticated user."""
        serializer = TwoFactorCodeInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                ErrorOutputSerializer({"error": "Invalid input data"}).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        verification_code = serializer.validated_data['code']
        
        try:
            is_valid = TwoFactorService.verify_code(verification_code)
            
            if is_valid:
                logger.info(f"2FA code verified successfully for user {request.user.id}")
            else:
                logger.warning(f"Invalid 2FA code attempt for user {request.user.id}")
            
            response_data = {
                "valid": is_valid,
                "message": "Code verified successfully" if is_valid else "Invalid verification code"
            }
            serializer = TwoFactorVerifyOutputSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error verifying 2FA code for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorStatusApi(APIView):
    """
    API for getting 2FA status for the authenticated user.
    
    GET /api/users/two-factor/status/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get 2FA status for the authenticated user."""
        try:
            is_enabled = TwoFactorService.is_2fa_enabled(request.user)
            
            response_data = {
                "enabled": is_enabled,
                "message": "Two-factor authentication is enabled" if is_enabled else "Two-factor authentication is disabled"
            }
            serializer = TwoFactorStatusOutputSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting 2FA status for user {request.user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Internal server error"}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SmartLoginApi(APIView):
    """
    Smart login API that handles first step of 2FA login.
    Returns user's 2FA requirement status instead of JWT tokens.
    
    POST /api/users/smart-login/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Smart login endpoint that handles first step of 2FA login."""
        serializer = SmartLoginInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                ErrorOutputSerializer({"error": "Email and password are required"}).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = LoginService.authenticate_user(email, password)
        if not user:
            logger.warning(f"Failed login attempt for email: {email}")
            return Response(
                ErrorOutputSerializer({"error": "Invalid email or password"}).data,
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Create temporary session
        try:
            temp_session_id = LoginService.create_temporary_session(user)
            masked_email = LoginService.mask_email(user.email)
            
            logger.info(f"Smart login initiated for user {user.id}")
            
            response_data = {
                "requires_2fa": user.two_factor_enabled,
                "temp_session_id": temp_session_id,
                "delivery_method": "email",
                "masked_email": masked_email,
                "message": "Please complete 2FA verification" if user.two_factor_enabled else "Please verify or skip 2FA"
            }
            serializer = SmartLoginOutputSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in smart login for user {user.id}: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Login failed. Please try again."}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SmartLoginVerifyApi(APIView):
    """
    Smart login verification API that handles 2FA verification with skip logic.
    Issues JWT tokens after successful verification.
    
    POST /api/users/smart-login/verify/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Smart login verification endpoint that handles 2FA verification with skip logic."""
        serializer = SmartLoginVerifyInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                ErrorOutputSerializer({"error": "Temporary session ID is required"}).data,
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_session_id = serializer.validated_data['temp_session_id']
        code = serializer.validated_data['code']
        skip = serializer.validated_data['skip']
        
        # Verify 2FA and complete login
        try:
            user = LoginService.verify_2fa_and_login(temp_session_id, code, skip)
            if not user:
                logger.warning(f"Failed 2FA verification for session: {temp_session_id}")
                return Response(
                    ErrorOutputSerializer({"error": "Invalid verification code or session expired"}).data,
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            logger.info(f"Smart login completed successfully for user {user.id}")
            
            response_data = {
                "access": str(access),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "two_factor_enabled": user.two_factor_enabled,
                },
                "message": "Login successful"
            }
            serializer = SmartLoginVerifyOutputSerializer(response_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in smart login verification: {str(e)}")
            return Response(
                ErrorOutputSerializer({"error": "Verification failed. Please try again."}).data,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
