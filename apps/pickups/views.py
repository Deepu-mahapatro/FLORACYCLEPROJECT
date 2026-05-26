"""
Pickup Request views:
  - Public POST  → anyone can submit a pickup request
  - Admin GET/PATCH → staff-only list + status management
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from apps.permissions import IsAdminRole
from .models import PickupRequest
from .serializers import (
    PickupRequestSerializer,
    PublicPickupSerializer,
    PickupStatusSerializer,
)
 
 
# ── Public: submit pickup ──────────────────────────────────────
class PickupCreateView(generics.CreateAPIView):
    """
    POST /api/v1/pickups/
    Anyone (including unauthenticated visitors) can submit a pickup request.
    """
    queryset           = PickupRequest.objects.all()
    serializer_class   = PublicPickupSerializer
    permission_classes = [permissions.AllowAny]
 
    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(submitted_by=user)
 
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {'message': 'Pickup request submitted successfully! Our team will confirm shortly.'},
            status=status.HTTP_201_CREATED
        )
 
 
# ── Admin: list all pickups ────────────────────────────────────
class PickupListView(generics.ListAPIView):
    queryset           = PickupRequest.objects.select_related('submitted_by')
    serializer_class   = PickupRequestSerializer
    permission_classes = [IsAdminRole]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status', 'flower_type']
    search_fields      = ['temple_name', 'full_name', 'location']
    ordering_fields    = ['pickup_date', 'submitted_on', 'quantity_kg']
    ordering           = ['-submitted_on']
 
 
class PickupDetailView(generics.RetrieveUpdateAPIView):
    queryset           = PickupRequest.objects.all()
    permission_classes = [IsAdminRole]
 
    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return PickupStatusSerializer
        return PickupRequestSerializer
 
 
class PickupStatsView(APIView):
    permission_classes = [IsAdminRole]
 
    def get(self, request):
        from django.db.models import Sum, Count
        qs = PickupRequest.objects.all()
        data = {
            'total_requests':   qs.count(),
            'pending':          qs.filter(status='Pending').count(),
            'approved':         qs.filter(status='Approved').count(),
            'collected':        qs.filter(status='Collected').count(),
            'completed':        qs.filter(status='Completed').count(),
            'total_flowers_kg': float(
                qs.aggregate(total=Sum('quantity_kg'))['total'] or 0
            ),
        }
        return Response(data)
