from django.urls import path
from .views import dashboard_summary, ventas_por_dia, compras_resumen, cash_por_categoria

app_name = 'reports'

urlpatterns = [
    path('dashboard/', dashboard_summary, name='dashboard'),
    path('ventas-por-dia/', ventas_por_dia, name='ventas-por-dia'),
    path('compras/', compras_resumen, name='compras'),
    path('cash-por-categoria/', cash_por_categoria, name='cash-por-categoria'),
]
