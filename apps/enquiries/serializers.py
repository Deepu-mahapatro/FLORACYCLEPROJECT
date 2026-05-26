from rest_framework import serializers
from .models import Enquiry
 
 
class EnquirySerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
 
    class Meta:
        model  = Enquiry
        fields = [
            'id', 'product', 'product_name',
            'customer_name', 'email', 'phone', 'quantity', 'message',
            'is_responded', 'submitted_on',
        ]
        read_only_fields = ['id', 'submitted_on']
 
    def get_product_name(self, obj):
        return obj.product.name if obj.product else 'General Enquiry'
 
    def validate_phone(self, value):
        import re
        if not re.match(r'^[6-9]\d{9}$', value.strip()):
            raise serializers.ValidationError('Enter a valid 10-digit Indian mobile number.')
        return value
 
    def validate_email(self, value):
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', value):
            raise serializers.ValidationError('Enter a valid email address.')
        return value