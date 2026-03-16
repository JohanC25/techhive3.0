from rest_framework.routers import DefaultRouter
from .views import CashSessionViewSet, CashMovementViewSet

app_name = 'cash_management'

router = DefaultRouter()
router.register(r'sessions', CashSessionViewSet, basename='session')
router.register(r'movements', CashMovementViewSet, basename='movement')

urlpatterns = router.urls
