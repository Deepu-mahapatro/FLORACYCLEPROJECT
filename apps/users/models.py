"""
Custom User model for FloraCycle.
Supports two roles: 'admin' (manufacturer/staff) and 'partner' (temple/vendor).
Also includes UserSettings for persistent admin configuration.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin',   'Admin / Manufacturer'),
        ('partner', 'Temple / Venue Partner'),
    ]

    email      = models.EmailField(unique=True)
    full_name  = models.CharField(max_length=120)
    phone      = models.CharField(max_length=15, blank=True)
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES, default='partner')
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        db_table = 'fc_users'
        verbose_name = 'User'

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class UserSettings(models.Model):
    """
    Persistent settings for each user, stored in the database.
    Auto-created when a new user registers.
    """
    user  = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    # General / Organisation settings
    org   = models.CharField(max_length=200, default='FloraCycle')
    email = models.EmailField(max_length=254, default='hello@floracycle.in')
    phone = models.CharField(max_length=30, default='+91 88888 88888')
    city  = models.CharField(max_length=120, default='Pune, Maharashtra')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fc_user_settings'
        verbose_name = 'User Settings'

    def __str__(self):
        return f'Settings for {self.user.email}'


# ── Auto-create settings row whenever a new User is saved ──────
@receiver(post_save, sender=User)
def create_user_settings(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.get_or_create(user=instance)
