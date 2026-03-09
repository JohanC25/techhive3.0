from rest_framework.permissions import BasePermission


class IsNotClient(BasePermission):
    """
    Bloquea a usuarios con rol 'client'.
    Los clientes solo pueden acceder al catálogo público.
    """
    message = "Los clientes no tienen acceso a esta sección."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', '') != 'client'
        )
