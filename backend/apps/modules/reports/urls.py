from django.urls import path
from .views import dashboard_summary, ventas_por_dia, compras_resumen

app_name = 'reports'

urlpatterns = [
    path('dashboard/', dashboard_summary, name='dashboard'),
    path('ventas-por-dia/', ventas_por_dia, name='ventas-por-dia'),
    path('compras/', compras_resumen, name='compras'),
]
