import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User, UserProfile
from users.services import TwoFactorService, UserService

User = get_user_model()


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def admin_user():
    """Fixture for admin user."""
    return UserService.create_user(
        email="admin@example.com",
        password="testpass123",
        first_name="Admin",
        last_name="User",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def contractor_user():
    """Fixture for contractor user."""
    return UserService.create_user(
        email="contractor@example.com",
        password="testpass123",
        first_name="Contractor",
        last_name="User",
        role=User.Role.CONTRACTOR,
    )


@pytest.mark.django_db
class TestUserListAPIView:
    """Test cases for UserListAPIView."""

    def test_admin_can_list_all_users(self, api_client, admin_user, contractor_user):
        """Test that admin users can list all users."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_contractor_gets_own_info(self, api_client, contractor_user):
        """Test that contractor users get their own info only."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == contractor_user.email

    def test_unauthenticated_access_denied(self, api_client):
        """Test that unauthenticated users cannot access the endpoint."""
        response = api_client.get("/api/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserDetailAPIView:
    """Test cases for UserDetailAPIView."""

    def test_admin_can_view_any_user(self, api_client, admin_user, contractor_user):
        """Test that admin can view any user's details."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/users/{contractor_user.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == contractor_user.email

    def test_user_can_view_own_details(self, api_client, contractor_user):
        """Test that users can view their own details."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get(f"/api/users/{contractor_user.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == contractor_user.email

    def test_user_cannot_view_other_user_details(
        self, api_client, admin_user, contractor_user
    ):
        """Test that users cannot view other users' details."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get(f"/api/users/{admin_user.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_details(self, api_client, contractor_user):
        """Test updating user details."""
        api_client.force_authenticate(user=contractor_user)
        data = {"first_name": "Updated"}
        response = api_client.patch(f"/api/users/{contractor_user.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"

    def test_nonexistent_user_returns_404(self, api_client, admin_user):
        """Test that accessing nonexistent user returns 404."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/users/99999/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUserCreateAPIView:
    """Test cases for UserCreateAPIView."""

    def test_admin_can_create_user(self, api_client, admin_user):
        """Test that admin can create new users."""
        api_client.force_authenticate(user=admin_user)
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": User.Role.CONTRACTOR,
        }
        response = api_client.post("/api/users/create/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "newuser@example.com"
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_contractor_cannot_create_user(self, api_client, contractor_user):
        """Test that contractors cannot create users."""
        api_client.force_authenticate(user=contractor_user)
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/users/create/", data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_missing_required_fields(self, api_client, admin_user):
        """Test creating user with missing required fields."""
        api_client.force_authenticate(user=admin_user)
        data = {"email": "incomplete@example.com"}
        response = api_client.post("/api/users/create/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_unauthenticated_cannot_create_user(self, api_client):
        """Test that unauthenticated users cannot create users."""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post("/api/users/create/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserRoleUpdateAPIView:
    """Test cases for UserRoleUpdateAPIView."""

    def test_admin_can_update_user_role(self, api_client, admin_user, contractor_user):
        """Test that admin can update user roles."""
        api_client.force_authenticate(user=admin_user)
        data = {"role": User.Role.ADMIN}
        response = api_client.post(f"/api/users/{contractor_user.id}/role/", data)

        assert response.status_code == status.HTTP_200_OK
        contractor_user.refresh_from_db()
        assert contractor_user.role == User.Role.ADMIN

    def test_contractor_cannot_update_role(
        self, api_client, contractor_user, admin_user
    ):
        """Test that contractors cannot update user roles."""
        api_client.force_authenticate(user=contractor_user)
        data = {"role": User.Role.ADMIN}
        response = api_client.post(f"/api/users/{admin_user.id}/role/", data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_role_missing_role_field(
        self, api_client, admin_user, contractor_user
    ):
        """Test updating role without providing role field."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(f"/api/users/{contractor_user.id}/role/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_update_role_nonexistent_user(self, api_client, admin_user):
        """Test updating role for nonexistent user."""
        api_client.force_authenticate(user=admin_user)
        data = {"role": User.Role.ADMIN}
        response = api_client.post("/api/users/99999/role/", data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUserActivateDeactivateAPIView:
    """Test cases for User Activate/Deactivate API Views."""

    def test_admin_can_activate_user(self, api_client, admin_user, contractor_user):
        """Test that admin can activate users."""
        contractor_user.is_active = False
        contractor_user.save()

        api_client.force_authenticate(user=admin_user)
        response = api_client.post(f"/api/users/{contractor_user.id}/activate/")

        assert response.status_code == status.HTTP_200_OK
        contractor_user.refresh_from_db()
        assert contractor_user.is_active is True

    def test_admin_can_deactivate_user(self, api_client, admin_user, contractor_user):
        """Test that admin can deactivate users."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(f"/api/users/{contractor_user.id}/deactivate/")

        assert response.status_code == status.HTTP_200_OK
        contractor_user.refresh_from_db()
        assert contractor_user.is_active is False

    def test_contractor_cannot_activate_user(
        self, api_client, contractor_user, admin_user
    ):
        """Test that contractors cannot activate users."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post(f"/api/users/{admin_user.id}/activate/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_contractor_cannot_deactivate_user(
        self, api_client, contractor_user, admin_user
    ):
        """Test that contractors cannot deactivate users."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post(f"/api/users/{admin_user.id}/deactivate/")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserProfileAPIView:
    """Test cases for UserProfileAPIView."""

    def test_get_user_profile(self, api_client, contractor_user):
        """Test getting user profile."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/profile/")

        assert response.status_code == status.HTTP_200_OK
        assert "bio" in response.data
        assert "avatar" in response.data

    def test_update_user_profile(self, api_client, contractor_user):
        """Test updating user profile."""
        api_client.force_authenticate(user=contractor_user)
        data = {"bio": "Updated bio"}
        response = api_client.patch("/api/users/profile/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "Updated bio"

    def test_unauthenticated_cannot_access_profile(self, api_client):
        """Test that unauthenticated users cannot access profile."""
        response = api_client.get("/api/users/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTwoFactorSetupAPIView:
    """Test cases for TwoFactorSetupAPIView."""

    def test_get_2fa_status(self, api_client, contractor_user):
        """Test getting 2FA status."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/2fa/setup/")

        assert response.status_code == status.HTTP_200_OK
        assert "two_factor_enabled" in response.data
        assert "two_factor_method" in response.data
        assert "can_use_sms" in response.data

    def test_enable_2fa(self, api_client, contractor_user):
        """Test enabling 2FA."""
        api_client.force_authenticate(user=contractor_user)
        data = {"enable": True, "method": UserProfile.TwoFactorMethod.EMAIL}
        response = api_client.post("/api/users/2fa/setup/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert TwoFactorService.is_2fa_enabled(contractor_user)

    def test_disable_2fa(self, api_client, contractor_user):
        """Test disabling 2FA."""
        # First enable 2FA
        TwoFactorService.enable_2fa(contractor_user)

        api_client.force_authenticate(user=contractor_user)
        data = {"enable": False}
        response = api_client.post("/api/users/2fa/setup/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert not TwoFactorService.is_2fa_enabled(contractor_user)


@pytest.mark.django_db
class TestTwoFactorRequestCodeAPIView:
    """Test cases for TwoFactorRequestCodeAPIView."""

    def test_request_2fa_code_when_enabled(self, api_client, contractor_user):
        """Test requesting 2FA code when 2FA is enabled."""
        TwoFactorService.enable_2fa(contractor_user)

        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/2fa/request-code/")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "expires_at" in response.data

    def test_request_2fa_code_when_disabled(self, api_client, contractor_user):
        """Test requesting 2FA code when 2FA is disabled."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/2fa/request-code/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data


@pytest.mark.django_db
class TestTwoFactorVerifyAPIView:
    """Test cases for TwoFactorVerifyAPIView."""

    def test_verify_valid_2fa_code(self, api_client, contractor_user):
        """Test verifying a valid 2FA code."""
        TwoFactorService.enable_2fa(contractor_user)
        code_obj = TwoFactorService.create_2fa_code(contractor_user)

        api_client.force_authenticate(user=contractor_user)
        data = {"code": code_obj.code}
        response = api_client.post("/api/users/2fa/verify/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["verified"] is True

    def test_verify_invalid_2fa_code(self, api_client, contractor_user):
        """Test verifying an invalid 2FA code."""
        TwoFactorService.enable_2fa(contractor_user)

        api_client.force_authenticate(user=contractor_user)
        data = {"code": "999999"}
        response = api_client.post("/api/users/2fa/verify/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["verified"] is False

    def test_verify_2fa_code_missing_code(self, api_client, contractor_user):
        """Test verifying 2FA code without providing code."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.post("/api/users/2fa/verify/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordChangeAPIView:
    """Test cases for PasswordChangeAPIView."""

    def test_change_password_success(self, api_client, contractor_user):
        """Test successful password change."""
        api_client.force_authenticate(user=contractor_user)
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = api_client.post("/api/users/change-password/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    def test_change_password_wrong_old_password(self, api_client, contractor_user):
        """Test password change with wrong old password."""
        api_client.force_authenticate(user=contractor_user)
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "confirm_password": "newpass123",
        }
        response = api_client.post("/api/users/change-password/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_mismatched_confirmation(self, api_client, contractor_user):
        """Test password change with mismatched confirmation."""
        api_client.force_authenticate(user=contractor_user)
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "confirm_password": "differentpass",
        }
        response = api_client.post("/api/users/change-password/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAdminStatsAPIView:
    """Test cases for AdminStatsAPIView."""

    def test_admin_can_access_stats(self, api_client, admin_user, contractor_user):
        """Test that admin can access statistics."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/users/admin/stats/")

        assert response.status_code == status.HTTP_200_OK
        assert "total_users" in response.data
        assert "admin_users" in response.data
        assert "contractor_users" in response.data
        assert "active_users" in response.data
        assert "users_with_2fa" in response.data
        assert response.data["total_users"] == 2

    def test_contractor_cannot_access_stats(self, api_client, contractor_user):
        """Test that contractors cannot access statistics."""
        api_client.force_authenticate(user=contractor_user)
        response = api_client.get("/api/users/admin/stats/")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_stats(self, api_client):
        """Test that unauthenticated users cannot access statistics."""
        response = api_client.get("/api/users/admin/stats/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
