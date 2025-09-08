from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin configuration for the User model.
    """
    
    # Fields to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_superuser', 'two_factor_enabled', 'created_at')
    list_filter = ('role', 'is_staff', 'is_superuser', 'two_factor_enabled', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    # Fields to display in the admin detail view
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Security'), {'fields': ('two_factor_enabled',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields to display when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    # Use email as the username field
    username_field = 'email'
