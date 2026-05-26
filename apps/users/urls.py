from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    UserListView,
    UserSettingsView,
)

urlpatterns = [
    path('register/',        RegisterView.as_view(),       name='auth-register'),
    path('login/',           LoginView.as_view(),          name='auth-login'),
    path('logout/',          LogoutView.as_view(),         name='auth-logout'),
    path('refresh/',         TokenRefreshView.as_view(),   name='auth-refresh'),
    path('profile/',         ProfileView.as_view(),        name='auth-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('users/',           UserListView.as_view(),       name='auth-user-list'),
    path('settings/',        UserSettingsView.as_view(),   name='auth-settings'),
]
