from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('historial/<str:session_id>/', views.historial_sesion, name='historial'),
    path('historial/<str:session_id>/limpiar/', views.limpiar_sesion, name='limpiar'),
    path('health/', views.health_check, name='health'),
]
