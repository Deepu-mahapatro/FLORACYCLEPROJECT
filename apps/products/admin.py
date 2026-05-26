from django.contrib import admin
from .models import Product
 
 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'emoji', 'eco_score', 'price', 'is_active', 'created_at']
    list_filter   = ['is_active', 'eco_score']
    search_fields = ['name', 'description']
    ordering      = ['name']
    readonly_fields = ['created_at', 'updated_at']
 
    fieldsets = (
        ('Basic',         {'fields': ('name', 'emoji', 'color', 'image', 'is_active')}),
        ('Description',   {'fields': ('description', 'full_desc')}),
        ('Eco Info',      {'fields': ('eco_benefit', 'eco_score', 'impact', 'ingredients')}),
        ('Pricing',       {'fields': ('price',)}),
        ('Usage',         {'fields': ('usage',)}),
        ('Timestamps',    {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
 
    actions = ['activate_products', 'deactivate_products']
 
    @admin.action(description='Activate selected products')
    def activate_products(self, request, queryset):
        queryset.update(is_active=True)
 
    @admin.action(description='Deactivate selected products')
    def deactivate_products(self, request, queryset):
        queryset.update(is_active=False)
