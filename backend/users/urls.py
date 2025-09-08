from django.urls import path
from .views import (
    UserStatsApi,
    TwoFactorSetupApi,
    TwoFactorEnableApi,
    TwoFactorDisableApi,
    TwoFactorVerifyApi,
    TwoFactorStatusApi,
    SmartLoginApi,
    SmartLoginVerifyApi,
)

app_name = "users"

urlpatterns = [
    path("stats/", UserStatsApi.as_view(), name="user-stats"),
    
    # Two-Factor Authentication endpoints
    path("two-factor/setup/", TwoFactorSetupApi.as_view(), name="2fa-setup"),
    path("two-factor/enable/", TwoFactorEnableApi.as_view(), name="2fa-enable"),
    path("two-factor/disable/", TwoFactorDisableApi.as_view(), name="2fa-disable"),
    path("two-factor/verify/", TwoFactorVerifyApi.as_view(), name="2fa-verify"),
    path("two-factor/status/", TwoFactorStatusApi.as_view(), name="2fa-status"),
    
    # Smart Login endpoints
    path("smart-login/", SmartLoginApi.as_view(), name="smart-login"),
    path("smart-login/verify/", SmartLoginVerifyApi.as_view(), name="smart-login-verify"),
]
