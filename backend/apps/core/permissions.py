from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Solo acceso a administradores"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')

class IsSellerUser(permissions.BasePermission):
    """Permite acceso a vendedores y administradores."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.role in ['ADMIN', 'SELLER'])

class IsOwnerOrAdmin(permissions.BasePermission):
    """Permite al dueño del objeto o al admin acceder/editar."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        # Asumiendo que el objeto tiene un campo 'user' o 'owner'
        return obj.user == request.user