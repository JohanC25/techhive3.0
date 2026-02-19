from django.urls import path
from .views import SalesHealthCheckView

app_name = "sales"

urlpatterns = [
    path("health/", SalesHealthCheckView.as_view(), name="health"),
]
