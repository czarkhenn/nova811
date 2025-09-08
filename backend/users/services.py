"""
Business logic is encapsulated in services.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
import secrets
import string

User = get_user_model()


class PermissionService:
    """
    Service for handling user permissions and authorization.
    """
    
    @staticmethod
    def can_view_user_stats(user):
        """
        Check if user can view user statistics.
        Only admin and manager roles can view stats.
        """
        return user.is_authenticated and user.role in ['admin', 'manager']


class TwoFactorService:
    """
    Service for handling Two-Factor Authentication operations.
    """
    
    # Mock verification code for development
    MOCK_VERIFICATION_CODE = "1234"
    
    @staticmethod
    def get_setup_data(user):
        """
        Get 2FA setup data including QR code and instructions.
        For now, returns mock data for development.
        """
        if not user.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        # Mock setup data - in production, this would generate real TOTP secrets
        return {
            "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
            "secret_key": "JBSWY3DPEHPK3PXP",  # Mock secret
            "backup_codes": ["123456", "789012", "345678", "901234", "567890"],
            "instructions": "Scan the QR code with your authenticator app, then enter the verification code to enable 2FA."
        }
    
    @staticmethod
    def enable_2fa(user):
        """
        Enable 2FA for the given user.
        """
        if not user.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        user.two_factor_enabled = True
        user.save(update_fields=['two_factor_enabled'])
        
        return True
    
    @staticmethod
    def disable_2fa(user):
        """
        Disable 2FA for the given user.
        """
        if not user.is_authenticated:
            raise ValidationError("User must be authenticated")
        
        user.two_factor_enabled = False
        user.save(update_fields=['two_factor_enabled'])
        
        return True
    
    @staticmethod
    def verify_code(code):
        """
        Verify a 2FA code.
        For development, accepts the mock code "1234".
        In production, this would verify against TOTP.
        """
        if not code:
            return False
        
        # Mock verification - accepts "1234" as valid
        return code == TwoFactorService.MOCK_VERIFICATION_CODE
    
    @staticmethod
    def is_2fa_enabled(user):
        """
        Check if 2FA is enabled for the given user.
        """
        if not user.is_authenticated:
            return False
        
        return user.two_factor_enabled


class LoginService:
    """
    Service for handling smart login with conditional 2FA.
    """
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with email and password.
        Returns user object if valid, None otherwise.
        """
        try:
            user = authenticate(username=email, password=password)
            return user
        except Exception:
            return None
    
    @staticmethod
    def mask_email(email):
        """
        Mask email address for privacy.
        Example: john.doe@gmail.com -> j***@gmail.com
        """
        if not email or '@' not in email:
            return email
        
        local_part, domain = email.split('@', 1)
        if len(local_part) <= 1:
            masked_local = local_part
        else:
            masked_local = local_part[0] + '***'
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def create_temporary_session(user):
        """
        Create a temporary session for 2FA verification.
        Returns a temporary session ID that expires in 5 minutes.
        """
        # Generate a secure random session ID
        session_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        
        # Store in Django session with expiration
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session['temp_user_id'] = user.id
        session['temp_login_time'] = timezone.now().isoformat()
        session.set_expiry(300)  # 5 minutes
        session.save()
        
        return session.session_key
    
    @staticmethod
    def get_user_from_temp_session(session_id):
        """
        Retrieve user from temporary session.
        Returns user object if session is valid, None otherwise.
        """
        try:
            from django.contrib.sessions.backends.db import SessionStore
            session = SessionStore(session_key=session_id)
            
            temp_user_id = session.get('temp_user_id')
            temp_login_time = session.get('temp_login_time')
            
            if not temp_user_id or not temp_login_time:
                return None
            
            # Check if session has expired (5 minutes)
            login_time = timezone.datetime.fromisoformat(temp_login_time.replace('Z', '+00:00'))
            if timezone.now() - login_time > timedelta(minutes=5):
                session.delete()
                return None
            
            user = User.objects.get(id=temp_user_id)
            return user
            
        except (User.DoesNotExist, Exception):
            return None
    
    @staticmethod
    def cleanup_temp_session(session_id):
        """
        Clean up temporary session after successful login.
        """
        try:
            from django.contrib.sessions.backends.db import SessionStore
            session = SessionStore(session_key=session_id)
            session.delete()
        except Exception:
            pass  # Session might already be expired/deleted
    
    @staticmethod
    def verify_2fa_and_login(session_id, code, skip=False):
        """
        Verify 2FA code and complete login process.
        Returns user object if successful, None otherwise.
        """
        user = LoginService.get_user_from_temp_session(session_id)
        if not user:
            return None
        
        # Check if user has 2FA enabled
        if user.two_factor_enabled:
            # 2FA is required - skip is not allowed
            if skip:
                return None
            
            # Verify the code
            if not TwoFactorService.verify_code(code):
                return None
        else:
            # 2FA is not required - user can skip or provide code
            if not skip and code:
                # User provided code, verify it
                if not TwoFactorService.verify_code(code):
                    return None
            # If skip=True or no code provided, allow login
        
        # Clean up temporary session
        LoginService.cleanup_temp_session(session_id)
        
        return user
