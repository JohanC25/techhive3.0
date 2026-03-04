from rest_framework.routers import DefaultRouter
from .views import VentaViewSet

app_name = 'sales'

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='venta')

urlpatterns = router.urls
