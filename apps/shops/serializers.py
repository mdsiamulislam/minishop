from rest_framework import serializers
from apps.shops.models import Shop

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'owner', 'phone', 'address', 'is_active']
        read_only_fields = ['id', 'owner', 'is_active']