"""
FloraCycle — Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
 
urlpatterns = [
    # ── Django admin ──────────────────────────────────────────
    path('admin/', admin.site.urls),
 
    # ── Frontend pages (served as templates) ──────────────────
    path('',           TemplateView.as_view(template_name='index.html'),     name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
 
    # ── REST API v1 ───────────────────────────────────────────
    path('api/v1/auth/',      include('apps.users.urls')),
    path('api/v1/pickups/',   include('apps.pickups.urls')),
    path('api/v1/enquiries/', include('apps.enquiries.urls')),
    path('api/v1/products/',  include('apps.products.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),
]
 
# ── Serve media files in development ──────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 
