from django.contrib import admin
from .models import Enquiry
 
 
@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display  = ['customer_name', 'email', 'phone', 'product', 'quantity', 'is_responded', 'submitted_on']
    list_filter   = ['is_responded', 'product']
    search_fields = ['customer_name', 'email', 'phone']
    ordering      = ['-submitted_on']
    readonly_fields = ['submitted_on']
 
    actions = ['mark_responded']
 
    @admin.action(description='Mark selected enquiries as responded')
    def mark_responded(self, request, queryset):
        queryset.update(is_responded=True)
