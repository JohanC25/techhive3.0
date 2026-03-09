from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg

from apps.core.permissions import IsNotClient
from .models import Venta
from .serializers import VentaSerializer


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated, IsNotClient]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descripcion', 'metodo_pago']
    ordering_fields = ['fecha_venta', 'total', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        metodo_pago = self.request.query_params.get('metodo_pago')

        if fecha_inicio:
            qs = qs.filter(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha_venta__lte=fecha_fin)
        if metodo_pago:
            qs = qs.filter(metodo_pago=metodo_pago)
        return qs

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """GET /api/sales/ventas/resumen/?fecha_inicio=&fecha_fin="""
        qs = self.get_queryset()
        agg = qs.aggregate(
            total_sum=Sum('total'),
            transacciones=Count('id'),
            promedio=Avg('total'),
        )
        return Response({
            'total': agg['total_sum'] or 0,
            'transacciones': agg['transacciones'],
            'promedio': agg['promedio'] or 0,
        })

    @action(detail=False, methods=['get'], url_path='por-producto')
    def por_producto(self, request):
        """GET /api/sales/ventas/por-producto/ — top productos por total vendido"""
        qs = self.get_queryset()
        datos = (
            qs.values('descripcion')
            .annotate(total=Sum('total'), cantidad=Sum('cantidad'), ventas=Count('id'))
            .order_by('-total')[:20]
        )
        return Response(list(datos))

    @action(detail=False, methods=['get'], url_path='por-metodo-pago')
    def por_metodo_pago(self, request):
        """GET /api/sales/ventas/por-metodo-pago/"""
        qs = self.get_queryset()
        datos = (
            qs.values('metodo_pago')
            .annotate(total=Sum('total'), ventas=Count('id'))
            .order_by('-total')
        )
        return Response(list(datos))
