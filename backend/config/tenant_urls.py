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
##from apps.users.serializers import CedulaTokenObtainPairSerializer

@api_view(["GET"])
def tenant_public_info(request):
    return Response({
        "company": request.tenant.name,
        "message": "Welcome to your tenant system",
    })

##class CedulaTokenObtainPairView(TokenObtainPairView):
##    serializer_class = CedulaTokenObtainPairSerializer

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Tenant APIs
    path("api/users/", include("apps.users.urls")),
    path("api/sales/", include("apps.modules.sales.urls")),
    path("api/inventory/", include("apps.modules.inventory.urls")),
    path("api/public-info/", tenant_public_info),

    # Auth endpoints
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/refresh/", TokenRefreshView.as_view(), name="refresh"),
]