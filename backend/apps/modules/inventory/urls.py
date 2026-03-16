from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ShelfViewSet, ProductViewSet

app_name = 'inventory'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'shelves', ShelfViewSet, basename='shelf')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = router.urls
