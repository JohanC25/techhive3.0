from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Q

from apps.core.permissions import IsNotClient
from .models import CashMovement
from .serializers import CashMovementSerializer


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
        """GET /api/cash/movements/balance/ — resumen de ingresos, egresos y balance"""
        qs = self.get_queryset()
        ingresos = qs.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
        egresos = qs.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        return Response({
            'ingresos': ingresos,
            'egresos': egresos,
            'balance': ingresos - egresos,
        })
