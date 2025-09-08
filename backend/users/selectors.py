"""
Contains query logic and data fetching operations.
"""

from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Q
from typing import Optional

User = get_user_model()


class UserSelector:
    """
    Selector for user-related queries.
    """

    @staticmethod
    def get_all_users() -> QuerySet[User]:
        """Get all users with basic optimization."""
        return User.objects.select_related().order_by('-date_joined')

    @staticmethod
    def get_users_by_role(role: str) -> QuerySet[User]:
        """Get users filtered by role."""
        return User.objects.filter(role=role).order_by('-date_joined')

    @staticmethod
    def get_active_users() -> QuerySet[User]:
        """Get only active users."""
        return User.objects.filter(is_active=True).order_by('-date_joined')

    @staticmethod
    def get_admin_users() -> QuerySet[User]:
        """Get users with admin role."""
        return UserSelector.get_users_by_role(User.Role.ADMIN)

    @staticmethod
    def get_contractor_users() -> QuerySet[User]:
        """Get users with contractor role."""
        return UserSelector.get_users_by_role(User.Role.CONTRACTOR)

    @staticmethod
    def search_users(query: str) -> QuerySet[User]:
        """
        Search users by email, first name, or last name.
        """
        if not query:
            return User.objects.none()

        return User.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        ).order_by('-date_joined')

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_users_for_admin_list() -> QuerySet[User]:
        """
        Includes necessary related data and ordering.
        """
        return User.objects.select_related().order_by(
            '-is_active', 'role', '-date_joined'
        )

    @staticmethod
    def get_user_count_by_role() -> dict:
        """
        Get count of users grouped by role.
        """
        from django.db.models import Count, Case, When, IntegerField

        result = User.objects.aggregate(
            total=Count('id'),
            admin_count=Count(
                Case(
                    When(role=User.Role.ADMIN, then=1),
                    output_field=IntegerField()
                )
            ),
            contractor_count=Count(
                Case(
                    When(role=User.Role.CONTRACTOR, then=1),
                    output_field=IntegerField()
                )
            ),
            active_count=Count(
                Case(
                    When(is_active=True, then=1),
                    output_field=IntegerField()
                )
            )
        )

        return {
            'total_users': result['total'],
            'admin_users': result['admin_count'],
            'contractor_users': result['contractor_count'],
            'active_users': result['active_count'],
            'inactive_users': result['total'] - result['active_count'],
        }

    @staticmethod
    def filter_users_for_role_management(requesting_user: User) -> QuerySet[User]:
        """
        Filter users that can be managed by the requesting user.
        Business rule: Admins can manage all users except themselves.
        """
        if not requesting_user.is_authenticated:
            return User.objects.none()

        if requesting_user.role == User.Role.ADMIN:
            # Admins can see all users but exclude themselves from role changes
            return User.objects.exclude(id=requesting_user.id).order_by('-date_joined')
        
        # Non-admins cannot manage users
        return User.objects.none()
