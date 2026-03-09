from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count

from apps.core.permissions import IsNotClient
from .models import ServiceTicket
from .serializers import ServiceTicketSerializer


class ServiceTicketViewSet(viewsets.ModelViewSet):
    queryset = ServiceTicket.objects.all()
    serializer_class = ServiceTicketSerializer
    permission_classes = [IsAuthenticated, IsNotClient]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['client_name', 'client_phone', 'device', 'serial_number']
    ordering_fields = ['created_at', 'priority', 'status', 'received_at']

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')

        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """GET /api/technical-service/tickets/resumen/ — conteo por estado"""
        qs = ServiceTicket.objects.values('status').annotate(total=Count('id'))
        return Response(list(qs))
