# users/decorators.py
from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.role not in allowed_roles:
                return Response({'error': 'No tienes permiso para acceder a esta vista.'}, status=status.HTTP_403_FORBIDDEN)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

