from django.contrib import admin
from apps.inventory.models import Category, Product

admin.site.register(Category)
admin.site.register(Product)

