from django.contrib import admin
from apps.transactions.models import Sale, SaleItem, Purchase, PurchaseItem



admin.site.register(Sale)
admin.site.register(SaleItem)

admin.site.register(Purchase)
admin.site.register(PurchaseItem)

# Register your models here.
