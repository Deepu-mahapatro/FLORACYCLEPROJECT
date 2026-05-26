from django.urls import path
from .views import PickupCreateView, PickupListView, PickupDetailView, PickupStatsView
 
urlpatterns = [
    path('',        PickupCreateView.as_view(), name='pickup-create'),   # POST (public)
    path('all/',    PickupListView.as_view(),   name='pickup-list'),     # GET  (admin)
    path('stats/',  PickupStatsView.as_view(),  name='pickup-stats'),    # GET  (admin)
    path('<int:pk>/', PickupDetailView.as_view(), name='pickup-detail'), # GET/PATCH (admin)
]
 