from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response

from apps.core.permissions import IsNotClient
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, ChangePasswordSerializer


class IsAdminOrManager(BasePermission):
    """Solo admin y manager pueden gestionar usuarios."""
    message = "Se requiere rol de administrador o gerente."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', '') in ('admin', 'manager')
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        # Acciones de escritura: solo admin/manager
        if self.action in ['create', 'destroy', 'update', 'partial_update']:
            return [IsAuthenticated(), IsAdminOrManager()]
        # me, modules, list, retrieve: cualquier usuario autenticado no-cliente
        if self.action in ['me', 'update_me', 'change_password', 'modules']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsNotClient()]

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """GET /api/users/me/ — perfil del usuario autenticado"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='me/update')
    def update_me(self, request):
        """PATCH /api/users/me/update/ — actualizar perfil propio"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='me/change-password')
    def change_password(self, request):
        """POST /api/users/me/change-password/"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Contraseña actualizada correctamente.'})

    @action(detail=False, methods=['get'], url_path='modules', permission_classes=[IsAuthenticated])
    def modules(self, request):
        """GET /api/users/modules/ — módulos habilitados para este tenant."""
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return Response([])
        return Response(list(tenant.modules.values('code', 'name')))
