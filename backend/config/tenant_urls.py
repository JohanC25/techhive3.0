# config/tenant_urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def tenant_landing(request):
    return Response({
        "page": f"Welcome {request.tenant.name}"
    })


urlpatterns = [
    path("admin/", admin.site.urls),

    # Tenant homepage
    path("", tenant_landing, name="tenant-landing"),

    # Auth endpoints
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/refresh/", TokenRefreshView.as_view(), name="refresh"),

    # Módulos
    path("api/users/", include("apps.users.urls")),
    path("api/sales/", include("apps.modules.sales.urls")),
    path("api/inventory/", include("apps.modules.inventory.urls")),
    path("api/purchases/", include("apps.modules.purchases.urls")),
    path("api/cash/", include("apps.modules.cash_management.urls")),
    path("api/technical-service/", include("apps.modules.technical_service.urls")),
    path("api/reports/", include("apps.modules.reports.urls")),

    # Chatbot
    path('api/chatbot/', include('apps.chatbot.urls')),

    # Predicción de ventas ML
    path('api/prediccion/', include('apps.prediccion.urls')),
]
