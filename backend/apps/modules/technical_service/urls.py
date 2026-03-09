from rest_framework.routers import DefaultRouter
from .views import ServiceTicketViewSet

app_name = 'technical_service'

router = DefaultRouter()
router.register(r'tickets', ServiceTicketViewSet, basename='ticket')

urlpatterns = router.urls
