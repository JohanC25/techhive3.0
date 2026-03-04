# config/public_urls.py

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.tenants.api import CompanyView


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/login/", TokenObtainPairView.as_view()),
    path("api/refresh/", TokenRefreshView.as_view()),

    path("api/companies/", CompanyView.as_view()),
]