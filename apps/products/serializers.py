from rest_framework import serializers
from .models import Product
 
 
class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
 
    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'emoji', 'description', 'full_desc',
            'eco_benefit', 'eco_score', 'price',
            'usage', 'impact', 'ingredients',
            'color', 'image', 'image_url', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']
 
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
 
 
class ProductListSerializer(serializers.ModelSerializer):
    """Compact serializer for public product cards."""
    image_url = serializers.SerializerMethodField()
 
    class Meta:
        model  = Product
        fields = ['id', 'name', 'emoji', 'description', 'eco_benefit',
                  'eco_score', 'price', 'color', 'image_url']
 
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None