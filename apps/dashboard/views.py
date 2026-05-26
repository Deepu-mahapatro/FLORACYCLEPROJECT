"""
Dashboard aggregate API — single endpoint that returns all stat-card data
plus recent pickups and enquiries for the admin overview.
"""
from django.db.models import Sum, Count
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.permissions import IsAdminRole
from apps.pickups.models import PickupRequest
from apps.enquiries.models import Enquiry
from apps.products.models import Product
from apps.pickups.serializers import PickupRequestSerializer
from apps.enquiries.serializers import EnquirySerializer
 
 
class DashboardSummaryView(APIView):
    """
    GET /api/v1/dashboard/summary/
    Returns all stat-card data, status breakdown, and recent rows.
    """
    permission_classes = [IsAdminRole]
 
    def get(self, request):
        pickups    = PickupRequest.objects.all()
        enquiries  = Enquiry.objects.all()
        products   = Product.objects.filter(is_active=True)
 
        total_flowers = float(
            pickups.aggregate(total=Sum('quantity_kg'))['total'] or 0
        )
 
        status_breakdown = list(
            pickups.values('status').annotate(count=Count('id'))
        )
 
        recent_pickups   = PickupRequestSerializer(
            pickups.order_by('-submitted_on')[:5], many=True,
            context={'request': request}
        ).data
 
        recent_enquiries = EnquirySerializer(
            enquiries.order_by('-submitted_on')[:5], many=True,
            context={'request': request}
        ).data
 
        return Response({
            'stats': {
                'total_pickups':    pickups.count(),
                'total_flowers_kg': total_flowers,
                'total_products':   products.count(),
                'total_enquiries':  enquiries.count(),
            },
            'pickup_status_breakdown': status_breakdown,
            'recent_pickups':          recent_pickups,
            'recent_enquiries':        recent_enquiries,
        })