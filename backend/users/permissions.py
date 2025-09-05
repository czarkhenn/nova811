from rest_framework import permissions

from .models import User
from .services import PermissionService


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to check if user has admin role.
    """

    def has_permission(self, request, view):
        return PermissionService.is_admin(request.user)


class IsContractorUser(permissions.BasePermission):
    """
    Permission class to check if user has contractor role.
    """

    def has_permission(self, request, view):
        return PermissionService.is_contractor(request.user)


class IsAdminOrContractor(permissions.BasePermission):
    """
    Permission class to check if user has admin or contractor role.
    """

    def has_permission(self, request, view):
        return PermissionService.is_admin(
            request.user
        ) or PermissionService.is_contractor(request.user)


class CanManageUsers(permissions.BasePermission):
    """
    Permission class to check if user can manage other users.
    """

    def has_permission(self, request, view):
        return PermissionService.can_manage_users(request.user)


class CanAccessAdminFeatures(permissions.BasePermission):
    """
    Permission class to check if user can access admin features.
    """

    def has_permission(self, request, view):
        return PermissionService.can_access_admin_features(request.user)


class CanCreateTickets(permissions.BasePermission):
    """
    Permission class to check if user can create tickets.
    """

    def has_permission(self, request, view):
        return PermissionService.can_create_tickets(request.user)


class CanManageTickets(permissions.BasePermission):
    """
    Permission class to check if user can manage all tickets.
    """

    def has_permission(self, request, view):
        return PermissionService.can_manage_tickets(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user is the owner of the object or an admin.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is admin
        if PermissionService.is_admin(request.user):
            return True

        # Check if user is the owner
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "owner"):
            return obj.owner == request.user
        elif isinstance(obj, User):
            return obj == request.user

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read access to all, but write access only to owner.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only to the owner
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "owner"):
            return obj.owner == request.user
        elif isinstance(obj, User):
            return obj == request.user

        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Custom permission class that checks permissions based on user roles.
    """

    # Define role-based permissions for different actions
    ROLE_PERMISSIONS = {
        "admin": [
            "view_user",
            "add_user",
            "change_user",
            "delete_user",
            "view_userprofile",
            "change_userprofile",
            "view_ticket",
            "add_ticket",
            "change_ticket",
            "delete_ticket",
        ],
        "contractor": [
            "view_user",
            "change_user",  # Can view and edit own profile
            "view_userprofile",
            "change_userprofile",  # Can manage own profile
            "view_ticket",
            "add_ticket",
            "change_ticket",  # Can manage own tickets
        ],
    }

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Get the required permission for this view/action
        required_permission = self.get_required_permission(request, view)

        if not required_permission:
            return True  # No specific permission required

        # Check if user's role has the required permission
        user_role = request.user.role
        role_permissions = self.ROLE_PERMISSIONS.get(user_role, [])

        return required_permission in role_permissions

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Admins can access everything
        if PermissionService.is_admin(request.user):
            return True

        # Users can only access their own objects
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif isinstance(obj, User):
            return obj == request.user

        return False

    def get_required_permission(self, request, view):
        """
        Get the required permission based on the request method and view.
        """
        action_map = {
            "GET": "view",
            "POST": "add",
            "PUT": "change",
            "PATCH": "change",
            "DELETE": "delete",
        }

        action = action_map.get(request.method, "view")

        # Try to get model name from view
        if hasattr(view, "queryset") and view.queryset is not None:
            model_name = view.queryset.model._meta.model_name
        elif hasattr(view, "model"):
            model_name = view.model._meta.model_name
        else:
            return None

        return f"{action}_{model_name}"
