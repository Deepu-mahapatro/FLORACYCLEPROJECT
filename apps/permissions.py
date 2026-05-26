"""
FloraCycle — Custom DRF Permission Classes
"""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to authenticated users whose role is 'admin'
    OR who are Django staff/superusers.

    Used to protect admin-only endpoints:
      - Pickup list / detail / stats
      - Enquiry list / detail
      - Dashboard summary
    """
    message = "Access restricted to admin users only."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                getattr(request.user, 'role', None) == 'admin'
                or request.user.is_staff
                or request.user.is_superuser
            )
        )
