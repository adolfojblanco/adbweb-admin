from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        user_role = getattr(request.user, 'role', None)
        return str(user_role).strip() == 'ADMIN'

class IsSellerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        return bool(
            request.user and
            request.user.is_authenticated and
            user_role in ['ADMIN', 'SELLER']
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'role', None) == 'ADMIN':
            return True
        # Verifica si el usuario es el dueño (ajusta 'user' según tu modelo)
        return getattr(obj, 'user', None) == request.user