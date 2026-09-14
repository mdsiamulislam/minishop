from django.db import models
from apps.shops.models import Shop
import os

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name


def product_image_upload_path(instance, filename):
    shop_id = instance.shop.id
    return os.path.join('products', str(shop_id), filename)

class Product(models.Model):
    shop = models.ForeignKey('shops.Shop', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, blank=True, null=True) # Barcode/SKU
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True)
    
    # Inventory
    stock = models.IntegerField(default=0)
    buy_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        # একই শপে একই SKU যেন বারবার না হয়
        unique_together = ('shop', 'sku')

    def __str__(self):
        return f"{self.name} ({self.shop.name})"
