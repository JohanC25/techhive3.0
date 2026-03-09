from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.tenants.views import (
    AdminLoginView,
    ModuleListView,
    CompanyListView,
    CompanyDetailView,
    CompanyModulesView,
)


def public_landing(request):
    return JsonResponse({"service": "TechHive SaaS", "status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", public_landing, name="public-landing"),

    # Admin portal auth
    path("api/admin/login/", AdminLoginView.as_view(), name="admin-login"),

    # Admin: módulos disponibles
    path("api/admin/modules/", ModuleListView.as_view(), name="admin-modules"),

    # Admin: gestión de empresas
    path("api/admin/companies/", CompanyListView.as_view(), name="admin-companies"),
    path("api/admin/companies/<int:pk>/", CompanyDetailView.as_view(), name="admin-company-detail"),
    path("api/admin/companies/<int:pk>/modules/", CompanyModulesView.as_view(), name="admin-company-modules"),

    # Tenant JWT (también disponible en schema público por compatibilidad)
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/refresh/", TokenRefreshView.as_view(), name="refresh"),
]
