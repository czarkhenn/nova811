from django.urls import path

from .views import (
    AdminStatsAPIView,
    PasswordChangeAPIView,
    TwoFactorMethodAPIView,
    TwoFactorRequestCodeAPIView,
    TwoFactorSetupAPIView,
    TwoFactorVerifyAPIView,
    UserActivateAPIView,
    UserCreateAPIView,
    UserDeactivateAPIView,
    UserDetailAPIView,
    UserListAPIView,
    UserProfileAPIView,
    UserRoleUpdateAPIView,
)

app_name = "users"

urlpatterns = [
    # User management
    path("", UserListAPIView.as_view(), name="user-list"),
    path("create/", UserCreateAPIView.as_view(), name="user-create"),
    path("<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("<int:pk>/role/", UserRoleUpdateAPIView.as_view(), name="user-role-update"),
    path("<int:pk>/activate/", UserActivateAPIView.as_view(), name="user-activate"),
    path(
        "<int:pk>/deactivate/", UserDeactivateAPIView.as_view(), name="user-deactivate"
    ),
    # User profile
    path("profile/", UserProfileAPIView.as_view(), name="user-profile"),
    # 2FA endpoints
    path("2fa/setup/", TwoFactorSetupAPIView.as_view(), name="2fa-setup"),
    path("2fa/method/", TwoFactorMethodAPIView.as_view(), name="2fa-method"),
    path(
        "2fa/request-code/",
        TwoFactorRequestCodeAPIView.as_view(),
        name="2fa-request-code",
    ),
    path("2fa/verify/", TwoFactorVerifyAPIView.as_view(), name="2fa-verify"),
    # Password management
    path("change-password/", PasswordChangeAPIView.as_view(), name="password-change"),
    # Admin endpoints
    path("admin/stats/", AdminStatsAPIView.as_view(), name="admin-stats"),
]
