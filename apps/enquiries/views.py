"""
Enquiry views.
  - Public  POST → anyone can submit a quote request
  - Admin   GET  → paginated list with filters
  - Admin   PATCH → mark as responded
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.permissions import IsAdminRole
from .models import Enquiry
from .serializers import EnquirySerializer
 
 
class EnquiryCreateView(generics.CreateAPIView):
    """
    POST /api/v1/enquiries/
    Public — submit a quote / product enquiry.
    """
    queryset           = Enquiry.objects.all()
    serializer_class   = EnquirySerializer
    permission_classes = [permissions.AllowAny]
 
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {'message': 'Request submitted successfully. Our manufacturer will contact you soon.'},
            status=status.HTTP_201_CREATED
        )
 
 
class EnquiryListView(generics.ListAPIView):
    queryset           = Enquiry.objects.select_related('product')
    serializer_class   = EnquirySerializer
    permission_classes = [IsAdminRole]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['is_responded', 'product']
    search_fields      = ['customer_name', 'email', 'phone']
    ordering           = ['-submitted_on']
 
 
class EnquiryDetailView(generics.RetrieveUpdateAPIView):
    queryset           = Enquiry.objects.all()
    serializer_class   = EnquirySerializer
    permission_classes = [IsAdminRole]