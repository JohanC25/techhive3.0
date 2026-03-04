from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from .models import Supplier, Purchase
from .serializers import SupplierSerializer, PurchaseSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'ruc', 'email']

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related('supplier').prefetch_related('items').all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['supplier__name', 'notes']
    ordering_fields = ['date', 'total', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        status = self.request.query_params.get('status')
        supplier = self.request.query_params.get('supplier')

        if fecha_inicio:
            qs = qs.filter(date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(date__lte=fecha_fin)
        if status:
            qs = qs.filter(status=status)
        if supplier:
            qs = qs.filter(supplier_id=supplier)
        return qs
