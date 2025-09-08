import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from users.services import TwoFactorService, LoginService

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def admin_user():
    """Fixture for admin user."""
    return User.objects.create_user(
        email="admin@example.com",
        password="testpass123",
        first_name="Admin",
        last_name="User",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def contractor_user():
    """Fixture for contractor user."""
    return User.objects.create_user(
        email="contractor@example.com",
        password="testpass123",
        first_name="Contractor",
        last_name="User",
        role=User.Role.CONTRACTOR,
    )


@pytest.mark.django_db
class TestUserStatsApi:
    """Test cases for UserStatsApi."""

    def test_admin_can_access_stats(self, api_client, admin_user, contractor_user):
        """Test that admin can access user statistics."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/users/stats/")

        assert response.status_code == status.HTTP_200_OK
        assert "total_users" in response.data
        assert "admin_users" in response.data
        assert "contractor_users" in response.data
        assert "active_users" in response.data
        assert "inactive_users" in response.data
        assert response.data["total_users"] == 2

    def test_contractor_cannot_access_stats(self, api_client, contractor_user):
        """Test that contractors cannot access statistics."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/stats/")

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "error" in response.data

    def test_unauthenticated_cannot_access_stats(self, api_client):
        """Test that unauthenticated users cannot access statistics."""
        response = api_client.get("/api/users/stats/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTwoFactorSetupApi:
    """Test cases for TwoFactorSetupApi."""

    def test_get_2fa_setup_data(self, api_client, contractor_user):
        """Test getting 2FA setup data."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/two-factor/setup/")

        assert response.status_code == status.HTTP_200_OK
        assert "qr_code" in response.data
        assert "secret_key" in response.data
        assert "backup_codes" in response.data
        assert "instructions" in response.data

    def test_unauthenticated_cannot_access_setup(self, api_client):
        """Test that unauthenticated users cannot access 2FA setup."""
        response = api_client.get("/api/users/two-factor/setup/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('users.services.TwoFactorService.get_setup_data')
    def test_setup_service_error_handling(self, mock_get_setup, api_client, contractor_user):
        """Test error handling in 2FA setup."""
        mock_get_setup.side_effect = Exception("Service error")
        
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/two-factor/setup/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data


@pytest.mark.django_db
class TestTwoFactorEnableApi:
    """Test cases for TwoFactorEnableApi."""

    def test_enable_2fa_with_valid_code(self, api_client, contractor_user):
        """Test enabling 2FA with valid verification code."""
        api_client.force_authenticate(user=contractor_user)
        data = {"code": "1234"}  # Mock valid code
        response = api_client.post("/api/users/two-factor/enable/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "enabled successfully" in response.data["message"]

    def test_enable_2fa_with_invalid_code(self, api_client, contractor_user):
        """Test enabling 2FA with invalid verification code."""
        api_client.force_authenticate(user=contractor_user)
        data = {"code": "9999"}  # Mock invalid code
        response = api_client.post("/api/users/two-factor/enable/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert "Invalid verification code" in response.data["error"]

    def test_enable_2fa_missing_code(self, api_client, contractor_user):
        """Test enabling 2FA without providing code."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/two-factor/enable/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_unauthenticated_cannot_enable_2fa(self, api_client):
        """Test that unauthenticated users cannot enable 2FA."""
        data = {"code": "1234"}
        response = api_client.post("/api/users/two-factor/enable/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTwoFactorDisableApi:
    """Test cases for TwoFactorDisableApi."""

    def test_disable_2fa(self, api_client, contractor_user):
        """Test disabling 2FA."""
        # First enable 2FA
        contractor_user.two_factor_enabled = True
        contractor_user.save()

        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/two-factor/disable/")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "disabled successfully" in response.data["message"]

    def test_unauthenticated_cannot_disable_2fa(self, api_client):
        """Test that unauthenticated users cannot disable 2FA."""
        response = api_client.post("/api/users/two-factor/disable/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('users.services.TwoFactorService.disable_2fa')
    def test_disable_service_error_handling(self, mock_disable, api_client, contractor_user):
        """Test error handling in 2FA disable."""
        mock_disable.side_effect = Exception("Service error")
        
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/two-factor/disable/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data


@pytest.mark.django_db
class TestTwoFactorVerifyApi:
    """Test cases for TwoFactorVerifyApi."""

    def test_verify_valid_2fa_code(self, api_client, contractor_user):
        """Test verifying a valid 2FA code."""
        api_client.force_authenticate(user=contractor_user)
        data = {"code": "1234"}  # Mock valid code
        response = api_client.post("/api/users/two-factor/verify/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["valid"] is True
        assert "verified successfully" in response.data["message"]

    def test_verify_invalid_2fa_code(self, api_client, contractor_user):
        """Test verifying an invalid 2FA code."""
        api_client.force_authenticate(user=contractor_user)
        data = {"code": "9999"}  # Mock invalid code
        response = api_client.post("/api/users/two-factor/verify/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["valid"] is False
        assert "Invalid verification code" in response.data["message"]

    def test_verify_2fa_code_missing_code(self, api_client, contractor_user):
        """Test verifying 2FA code without providing code."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/two-factor/verify/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_unauthenticated_cannot_verify_2fa(self, api_client):
        """Test that unauthenticated users cannot verify 2FA."""
        data = {"code": "1234"}
        response = api_client.post("/api/users/two-factor/verify/", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTwoFactorStatusApi:
    """Test cases for TwoFactorStatusApi."""

    def test_get_2fa_status_enabled(self, api_client, contractor_user):
        """Test getting 2FA status when enabled."""
        contractor_user.two_factor_enabled = True
        contractor_user.save()

        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/two-factor/status/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["enabled"] is True
        assert "enabled" in response.data["message"]

    def test_get_2fa_status_disabled(self, api_client, contractor_user):
        """Test getting 2FA status when disabled."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/two-factor/status/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["enabled"] is False
        assert "disabled" in response.data["message"]

    def test_unauthenticated_cannot_get_status(self, api_client):
        """Test that unauthenticated users cannot get 2FA status."""
        response = api_client.get("/api/users/two-factor/status/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSmartLoginApi:
    """Test cases for SmartLoginApi."""

    def test_smart_login_valid_credentials(self, api_client, contractor_user):
        """Test smart login with valid credentials."""
        data = {
            "email": "contractor@example.com",
            "password": "testpass123"
        }
        response = api_client.post("/api/users/smart-login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "requires_2fa" in response.data
        assert "temp_session_id" in response.data
        assert "delivery_method" in response.data
        assert "masked_email" in response.data
        assert "message" in response.data

    def test_smart_login_invalid_credentials(self, api_client):
        """Test smart login with invalid credentials."""
        data = {
            "email": "wrong@example.com",
            "password": "wrongpass"
        }
        response = api_client.post("/api/users/smart-login/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data
        assert "Invalid email or password" in response.data["error"]

    def test_smart_login_missing_credentials(self, api_client):
        """Test smart login with missing credentials."""
        data = {"email": "test@example.com"}  # Missing password
        response = api_client.post("/api/users/smart-login/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_smart_login_2fa_enabled_user(self, api_client, contractor_user):
        """Test smart login with 2FA enabled user."""
        contractor_user.two_factor_enabled = True
        contractor_user.save()

        data = {
            "email": "contractor@example.com",
            "password": "testpass123"
        }
        response = api_client.post("/api/users/smart-login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["requires_2fa"] is True
        assert "complete 2FA verification" in response.data["message"]

    def test_smart_login_2fa_disabled_user(self, api_client, contractor_user):
        """Test smart login with 2FA disabled user."""
        data = {
            "email": "contractor@example.com",
            "password": "testpass123"
        }
        response = api_client.post("/api/users/smart-login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["requires_2fa"] is False
        assert "verify or skip" in response.data["message"]

    @patch('users.services.LoginService.create_temporary_session')
    def test_smart_login_session_creation_error(self, mock_create_session, api_client, contractor_user):
        """Test smart login when session creation fails."""
        mock_create_session.side_effect = Exception("Session error")

        data = {
            "email": "contractor@example.com",
            "password": "testpass123"
        }
        response = api_client.post("/api/users/smart-login/", data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data


@pytest.mark.django_db
class TestSmartLoginVerifyApi:
    """Test cases for SmartLoginVerifyApi."""

    def test_smart_login_verify_success(self, api_client, contractor_user):
        """Test successful smart login verification."""
        # Create a temporary session
        session_id = LoginService.create_temporary_session(contractor_user)

        data = {
            "temp_session_id": session_id,
            "code": "",
            "skip": True
        }
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data
        assert "message" in response.data
        assert response.data["user"]["email"] == contractor_user.email

    def test_smart_login_verify_2fa_required_valid_code(self, api_client, contractor_user):
        """Test smart login verification with 2FA required and valid code."""
        contractor_user.two_factor_enabled = True
        contractor_user.save()

        session_id = LoginService.create_temporary_session(contractor_user)

        data = {
            "temp_session_id": session_id,
            "code": "1234",  # Mock valid code
            "skip": False
        }
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_smart_login_verify_2fa_required_invalid_code(self, api_client, contractor_user):
        """Test smart login verification with 2FA required and invalid code."""
        contractor_user.two_factor_enabled = True
        contractor_user.save()

        session_id = LoginService.create_temporary_session(contractor_user)

        data = {
            "temp_session_id": session_id,
            "code": "9999",  # Mock invalid code
            "skip": False
        }
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data
        assert "Invalid verification code" in response.data["error"]

    def test_smart_login_verify_2fa_required_skip_not_allowed(self, api_client, contractor_user):
        """Test smart login verification with 2FA required but user tries to skip."""
        contractor_user.two_factor_enabled = True
        contractor_user.save()

        session_id = LoginService.create_temporary_session(contractor_user)

        data = {
            "temp_session_id": session_id,
            "skip": True
        }
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data

    def test_smart_login_verify_invalid_session(self, api_client):
        """Test smart login verification with invalid session."""
        data = {
            "temp_session_id": "invalid-session-id",
            "skip": True
        }
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data

    def test_smart_login_verify_missing_session_id(self, api_client):
        """Test smart login verification without session ID."""
        data = {"skip": True}
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    @patch('users.services.LoginService.verify_2fa_and_login')
    def test_smart_login_verify_service_error(self, mock_verify, api_client, contractor_user):
        """Test smart login verification when service fails."""
        mock_verify.side_effect = Exception("Service error")

        session_id = LoginService.create_temporary_session(contractor_user)

        data = {
            "temp_session_id": session_id,
            "skip": True
        }
        response = api_client.post("/api/users/smart-login/verify/", data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data
