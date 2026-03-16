import datetime
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum

from apps.core.permissions import IsNotClient
from .models import CashMovement, CashSession
from .serializers import CashMovementSerializer, CashSessionSerializer


class CashSessionViewSet(viewsets.ModelViewSet):
    queryset = CashSession.objects.all()
    serializer_class = CashSessionSerializer
    permission_classes = [IsAuthenticated, IsNotClient]

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        """GET /api/cash/sessions/today/ — sesión de hoy o 404."""
        hoy = datetime.date.today()
        try:
            session = CashSession.objects.get(date=hoy)
            return Response(CashSessionSerializer(session).data)
        except CashSession.DoesNotExist:
            return Response({'detail': 'No hay sesión abierta para hoy.'}, status=status.HTTP_404_NOT_FOUND)


class CashMovementViewSet(viewsets.ModelViewSet):
    queryset = CashMovement.objects.all()
    serializer_class = CashMovementSerializer
    permission_classes = [IsAuthenticated, IsNotClient]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        type_ = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        if type_:
            qs = qs.filter(type=type_)
        if category:
            qs = qs.filter(category=category)
        if fecha_inicio:
            qs = qs.filter(date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(date__lte=fecha_fin)
        return qs

    @action(detail=False, methods=['get'], url_path='balance')
    def balance(self, request):
        """GET /api/cash/movements/balance/ — ingresos, egresos, monto inicial y caja final."""
        qs = self.get_queryset()
        ingresos = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        egresos = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0

        # Obtener monto inicial: sesión del día filtrado (o hoy si no hay filtro)
        monto_inicial = 0
        try:
            fecha_inicio = request.query_params.get('fecha_inicio')
            session_date = (
                datetime.date.fromisoformat(fecha_inicio)
                if fecha_inicio
                else datetime.date.today()
            )
            session = CashSession.objects.get(date=session_date)
            monto_inicial = session.opening_amount
        except (CashSession.DoesNotExist, ValueError):
            pass

        return Response({
            'monto_inicial': monto_inicial,
            'ingresos': ingresos,
            'egresos': egresos,
            'caja_final': monto_inicial + ingresos - egresos,
        })
