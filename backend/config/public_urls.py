# config/public_urls.py

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.tenants.views import CompanyListView

def public_landing(request):
    return JsonResponse({
        "company": "My SaaS Platform",
        "headline": "Manage Your Business Smarter",
        "subheadline": "Multi-tenant inventory & sales management system",
        "features": [
            "Inventory Management",
            "Sales Tracking",
            "Role-Based Access",
            "Analytics Dashboard"
        ]
    })

urlpatterns = [
    path("admin/", admin.site.urls),

    # Landing page (yoursaas.com)
    path("", public_landing, name="public-landing"),

    # Auth endpoints
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api/companies/", CompanyListView.as_view()),
]