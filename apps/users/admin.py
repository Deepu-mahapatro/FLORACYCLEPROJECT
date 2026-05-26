"""
FloraCycle — Custom User Admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
 
 
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Columns shown in the list view
    list_display  = ['email', 'full_name', 'phone', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter   = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'full_name', 'phone']
    ordering      = ['-created_at']
    readonly_fields = ['created_at', 'last_login']
 
    # Override default fieldsets to use email instead of username
    fieldsets = (
        (None,          {'fields': ('email', 'password')}),
        (_('Personal'), {'fields': ('full_name', 'phone', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Timestamps'), {'fields': ('created_at', 'last_login'), 'classes': ('collapse',)}),
    )
 
    # Fieldsets for the "add user" form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'role', 'password1', 'password2'),
        }),
    )
 
    # Required by BaseUserAdmin when USERNAME_FIELD is not 'username'
    filter_horizontal = ['groups', 'user_permissions']
 
    actions = ['activate_users', 'deactivate_users', 'make_admin']
 
    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} user(s) activated.')
 
    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} user(s) deactivated.')
 
    @admin.action(description='Set role to Admin')
    def make_admin(self, request, queryset):
        queryset.update(role='admin', is_staff=True)
        self.message_user(request, f'{queryset.count()} user(s) set as admin.')
 

from .models import UserSettings

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'org', 'email', 'phone', 'city', 'updated_at']
    search_fields = ['user__email', 'user__full_name', 'org']
    readonly_fields = ['updated_at']
