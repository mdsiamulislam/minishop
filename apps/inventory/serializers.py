from rest_framework import serializers
from apps.inventory.models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'shop']
        read_only_fields = ['id', 'shop']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'shop', 'category', 'name', 'sku', 'description', 'image', 'stock', 'buy_price', 'sell_price', 'is_active']
        read_only_fields = ['id', 'shop']