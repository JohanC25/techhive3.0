from datetime import date, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    GET /api/reports/dashboard/
    Resumen general del negocio: ventas, caja, inventario, tickets.
    Acepta ?fecha_inicio=&fecha_fin= (por defecto mes actual).
    """
    hoy = date.today()
    fecha_inicio = request.query_params.get('fecha_inicio', hoy.replace(day=1).isoformat())
    fecha_fin = request.query_params.get('fecha_fin', hoy.isoformat())

    # Ventas
    try:
        from apps.modules.sales.models import Venta
        ventas_qs = Venta.objects.filter(fecha_venta__range=[fecha_inicio, fecha_fin])
        ventas_agg = ventas_qs.aggregate(total_sum=Sum('total'), transacciones=Count('id'), promedio=Avg('total'))
    except Exception:
        ventas_agg = {'total_sum': 0, 'transacciones': 0, 'promedio': 0}

    # Caja
    try:
        from apps.modules.cash_management.models import CashMovement
        caja_qs = CashMovement.objects.filter(date__range=[fecha_inicio, fecha_fin])
        ingresos = caja_qs.filter(type='income').aggregate(t=Sum('amount'))['t'] or 0
        egresos = caja_qs.filter(type='expense').aggregate(t=Sum('amount'))['t'] or 0
    except Exception:
        ingresos, egresos = 0, 0

    # Inventario bajo stock
    try:
        from apps.modules.inventory.models import Product
        from django.db.models import F
        low_stock_count = Product.objects.filter(stock__lte=F('stock_min'), is_active=True).count()
        total_products = Product.objects.filter(is_active=True).count()
    except Exception:
        low_stock_count, total_products = 0, 0

    # Servicio técnico
    try:
        from apps.modules.technical_service.models import ServiceTicket
        tickets_abiertos = ServiceTicket.objects.exclude(status__in=['completed', 'delivered', 'cancelled']).count()
        tickets_completados = ServiceTicket.objects.filter(
            status__in=['completed', 'delivered'],
            completed_at__range=[fecha_inicio, fecha_fin]
        ).count()
    except Exception:
        tickets_abiertos, tickets_completados = 0, 0

    return Response({
        'periodo': {'inicio': fecha_inicio, 'fin': fecha_fin},
        'ventas': {
            'total': ventas_agg['total_sum'] or 0,
            'transacciones': ventas_agg['transacciones'] or 0,
            'promedio': ventas_agg['promedio'] or 0,
        },
        'caja': {
            'ingresos': ingresos,
            'egresos': egresos,
            'balance': ingresos - egresos,
        },
        'inventario': {
            'total_productos': total_products,
            'productos_stock_bajo': low_stock_count,
        },
        'servicio_tecnico': {
            'tickets_abiertos': tickets_abiertos,
            'tickets_completados_periodo': tickets_completados,
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ventas_por_dia(request):
    """
    GET /api/reports/ventas-por-dia/?fecha_inicio=&fecha_fin=
    Ventas agrupadas por día para gráficas.
    """
    hoy = date.today()
    fecha_inicio = request.query_params.get('fecha_inicio', (hoy - timedelta(days=29)).isoformat())
    fecha_fin = request.query_params.get('fecha_fin', hoy.isoformat())

    try:
        from apps.modules.sales.models import Venta
        datos = (
            Venta.objects
            .filter(fecha_venta__range=[fecha_inicio, fecha_fin])
            .values('fecha_venta')
            .annotate(total=Sum('total'), transacciones=Count('id'))
            .order_by('fecha_venta')
        )
        return Response(list(datos))
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compras_resumen(request):
    """
    GET /api/reports/compras/?fecha_inicio=&fecha_fin=
    """
    hoy = date.today()
    fecha_inicio = request.query_params.get('fecha_inicio', hoy.replace(day=1).isoformat())
    fecha_fin = request.query_params.get('fecha_fin', hoy.isoformat())

    try:
        from apps.modules.purchases.models import Purchase
        qs = Purchase.objects.filter(date__range=[fecha_inicio, fecha_fin])
        agg = qs.aggregate(total=Sum('total'), cantidad=Count('id'))
        by_status = list(
            qs.values('status')
            .annotate(total=Sum('total'), count=Count('id'))
            .order_by('status')
        )
        return Response({
            'total_amount': agg['total'] or 0,
            'total_purchases': agg['cantidad'],
            'by_status': by_status,
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
