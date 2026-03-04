from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseViewSet

app_name = 'purchases'

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'purchases', PurchaseViewSet, basename='purchase')

urlpatterns = router.urls
