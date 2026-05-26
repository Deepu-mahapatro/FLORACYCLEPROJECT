from rest_framework import serializers
from .models import PickupRequest
 
 
class PickupRequestSerializer(serializers.ModelSerializer):
    """Full serializer — used by admin/dashboard."""
    submitted_by_name = serializers.SerializerMethodField(read_only=True)
 
    class Meta:
        model  = PickupRequest
        fields = [
            'id', 'submitted_by', 'submitted_by_name',
            'full_name', 'temple_name', 'phone', 'location',
            'flower_type', 'quantity_kg', 'pickup_date',
            'status', 'admin_notes', 'submitted_on', 'updated_at',
        ]
        read_only_fields = ['id', 'submitted_by', 'submitted_on', 'updated_at']
 
    def get_submitted_by_name(self, obj):
        return obj.submitted_by.full_name if obj.submitted_by else None
 
 
class PublicPickupSerializer(serializers.ModelSerializer):
    """Minimal serializer for the public pickup form submission."""
 
    class Meta:
        model  = PickupRequest
        fields = [
            'id', 'full_name', 'temple_name', 'phone', 'location',
            'flower_type', 'quantity_kg', 'pickup_date', 'submitted_on',
        ]
        read_only_fields = ['id', 'submitted_on']
 
    def validate_quantity_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0.')
        return value
 
    def validate_phone(self, value):
        import re
        if not re.match(r'^[6-9]\d{9}$', value.strip()):
            raise serializers.ValidationError('Enter a valid 10-digit Indian mobile number.')
        return value
 
 
class PickupStatusSerializer(serializers.ModelSerializer):
    """Used by admin to update only status + notes."""
 
    class Meta:
        model  = PickupRequest
        fields = ['status', 'admin_notes']