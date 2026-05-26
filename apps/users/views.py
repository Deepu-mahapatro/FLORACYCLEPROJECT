"""
FloraCycle — User Authentication Views
Register · Login · Logout · Profile · Change Password · Admin List · Settings
"""
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.permissions import IsAdminRole

from .models import UserSettings
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserListSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    UserSettingsSerializer,
)

User = get_user_model()


# ── Register ───────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/auth/register/
    Creates a new user and immediately returns JWT tokens.
    No authentication required.
    """
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Account created successfully.',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


# ── Login ──────────────────────────────────────────────────────

class LoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    Returns access + refresh JWT tokens plus user info.
    Updates last_login on every successful login.
    No authentication required.
    """
    serializer_class   = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from django.utils import timezone
            email = request.data.get('email', '')
            try:
                user = User.objects.get(email=email.lower())
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
            except User.DoesNotExist:
                pass
        return response


# ── Logout ─────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token so it can't be reused.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Invalid or expired token: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ── Profile ────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/auth/profile/  — retrieve own profile
    PATCH /api/v1/auth/profile/  — update full_name / phone
    Requires authentication.
    """
    serializer_class   = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Change Password ────────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password/
    Body: { old_password, new_password, new_password2 }
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(
            {'message': 'Password changed successfully. Please log in again.'},
            status=status.HTTP_200_OK
        )


# ── Admin: list all users ──────────────────────────────────────

class UserListView(generics.ListAPIView):
    """
    GET /api/v1/auth/users/
    Admin-only: list all registered users (partners + admins).
    """
    queryset           = User.objects.all().order_by('-created_at')
    serializer_class   = UserListSerializer
    permission_classes = [IsAdminRole]


# ── User Settings (persistent, DB-backed) ─────────────────────

class UserSettingsView(APIView):
    """
    GET  /api/v1/auth/settings/  — fetch saved settings for logged-in user
    POST /api/v1/auth/settings/  — save/update settings for logged-in user

    Settings survive logout, refresh, and server restart because they
    are stored in the fc_user_settings DB table, not in localStorage.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(settings_obj)
        return Response(serializer.data)

    def post(self, request):
        settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Settings saved successfully.',
            'settings': serializer.data,
        })
