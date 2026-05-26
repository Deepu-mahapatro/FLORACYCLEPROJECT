from django.urls import path
from .views import EnquiryCreateView, EnquiryListView, EnquiryDetailView
 
urlpatterns = [
    path('',        EnquiryCreateView.as_view(), name='enquiry-create'),
    path('all/',    EnquiryListView.as_view(),   name='enquiry-list'),
    path('<int:pk>/', EnquiryDetailView.as_view(), name='enquiry-detail'),
]
 