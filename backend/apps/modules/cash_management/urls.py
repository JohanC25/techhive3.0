from rest_framework.routers import DefaultRouter
from .views import CashMovementViewSet

app_name = 'cash_management'

router = DefaultRouter()
router.register(r'movements', CashMovementViewSet, basename='movement')

urlpatterns = router.urls
