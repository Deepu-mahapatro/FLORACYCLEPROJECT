"""
Product views:
  - Public GET  → list active products (card view)
  - Public GET  → retrieve single product detail
  - Admin POST  → create a new product
  - Admin PATCH/DELETE → update or delete a product
"""
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from apps.permissions import IsAdminRole
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer


# ── Public: list all active products ──────────────────────────
class ProductListView(generics.ListAPIView):
    """
    GET /api/v1/products/
    Returns a compact card-friendly list of active products.
    No authentication required.
    """
    queryset           = Product.objects.filter(is_active=True)
    serializer_class   = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['name', 'description', 'eco_benefit']
    ordering_fields    = ['name', 'eco_score', 'created_at']
    ordering           = ['name']


# ── Public: product detail ─────────────────────────────────────
class ProductDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/products/<pk>/
    Returns full details for a single product.
    No authentication required.
    """
    queryset           = Product.objects.filter(is_active=True)
    serializer_class   = ProductSerializer
    permission_classes = [permissions.AllowAny]


# ── Admin: create product ──────────────────────────────────────
class ProductCreateView(generics.CreateAPIView):
    """
    POST /api/v1/products/create/
    Admin-only: add a new product to the catalogue.
    """
    queryset           = Product.objects.all()
    serializer_class   = ProductSerializer
    permission_classes = [IsAdminRole]


# ── Admin: update / delete product ────────────────────────────
class ProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/products/<pk>/manage/  → full detail (admin)
    PATCH  /api/v1/products/<pk>/manage/  → partial update
    DELETE /api/v1/products/<pk>/manage/  → soft-delete (sets is_active=False)
    """
    queryset           = Product.objects.all()
    serializer_class   = ProductSerializer
    permission_classes = [IsAdminRole]

    def perform_destroy(self, instance):
        # Soft delete — keeps the row, just hides it from public views
        instance.is_active = False
        instance.save()
