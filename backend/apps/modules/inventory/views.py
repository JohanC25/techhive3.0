from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'stock', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        category = self.request.query_params.get('category')
        low_stock = self.request.query_params.get('low_stock')

        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        if category:
            qs = qs.filter(category_id=category)
        if low_stock == 'true':
            from django.db.models import F
            qs = qs.filter(stock__lte=F('stock_min'))
        return qs

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """GET /api/inventory/products/low-stock/ — productos con stock bajo"""
        from django.db.models import F
        qs = self.get_queryset().filter(stock__lte=F('stock_min'), is_active=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
