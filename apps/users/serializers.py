"""
FloraCycle — Users Serializers
All user-related serializers in one place.

SECURITY: Admin role can ONLY be assigned via createsuperuser / Django shell.
          Public registration always creates a 'partner' account.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserSettings

User = get_user_model()


# ── Registration ──────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """Validates and creates a new partner user account.
    
    NOTE: The 'role' field is intentionally EXCLUDED from public registration.
    Admin accounts can ONLY be created via `python manage.py createsuperuser`.
    """
    password  = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        write_only=True,
        label='Confirm Password',
        style={'input_type': 'password'},
    )

    class Meta:
        model  = User
        # role is NOT in fields — public users are always 'partner'
        fields = ['email', 'full_name', 'phone', 'password', 'password2']
        extra_kwargs = {
            'email':     {'required': True},
            'full_name': {'required': True},
            'phone':     {'required': False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        # Always force role=partner regardless of any payload tampering
        validated_data['role'] = 'partner'
        return User.objects.create_user(**validated_data)


# ── Profile ────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    """Read/update own profile. Email and role are read-only after creation."""

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone     = validated_data.get('phone',     instance.phone)
        instance.save()
        return instance


# ── Admin list ─────────────────────────────────────────────────

class UserListSerializer(serializers.ModelSerializer):
    """Admin-only: full user list with last_login."""

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'is_active', 'created_at', 'last_login']
        read_only_fields = fields


# ── Custom JWT payload ─────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT login serializer to include user info
    in the token response, so the frontend knows the user's role
    without an extra /profile/ call.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id':        self.user.id,
            'email':     self.user.email,
            'full_name': self.user.full_name,
            'role':      self.user.role,
            'is_staff':  self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }
        return data


# ── Password change ────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    """Allows an authenticated user to change their password."""
    old_password  = serializers.CharField(required=True, write_only=True)
    new_password  = serializers.CharField(required=True, write_only=True, min_length=8,
                                          validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'New passwords do not match.'})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


# ── User Settings ──────────────────────────────────────────────

class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for persistent user settings stored in DB."""

    class Meta:
        model  = UserSettings
        fields = ['org', 'email', 'phone', 'city', 'updated_at']
        read_only_fields = ['updated_at']
