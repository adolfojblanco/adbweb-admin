"""
DRF permissions for the SEO module.

Kept self-contained: the module does not depend on ``apps.core``.
"""
from rest_framework import permissions


class IsSeoAdmin(permissions.BasePermission):
    """Only authenticated staff/admin users can access the SEO module."""

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return False
        if getattr(user, "is_admin", False):
            return True
        return bool(getattr(user, "is_staff", False))
