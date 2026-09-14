from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.transactions.models import Purchase, PurchaseItem
from apps.inventory.models import Product
from apps.shops.models import Shop


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supplier_name = request.data.get('supplier_name')
        product_id = request.data.get('product')
        
        # ১. ডাটা টাইপ কনভার্সন ও ভ্যালিডেশন
        try:
            quantity = int(request.data.get('quantity', 0))
            unit_buy_price = float(request.data.get('unit_buy_price', 0))
        except (ValueError, TypeError):
            return Response({"error": "Quantity and unit_buy_price must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0 or unit_buy_price < 0:
            return Response({"error": "Invalid quantity or price."}, status=status.HTTP_400_BAD_REQUEST)

        # ২. শপ চেক
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"error": "No shop found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        # ৩. প্রোডাক্টটি এই শপের কি না তা চেক
        try:
            product_instance = Product.objects.get(id=product_id, shop=shop)
        except Product.DoesNotExist:
            return Response({"error": "Product not found in your shop."}, status=status.HTTP_404_NOT_FOUND)

        total_amount = quantity * unit_buy_price

        # ৪. Atomic Transaction (সবগুলো একসাথে কাজ করবে, নয়তো কিছুই সেভ হবে না)
        try:
            with transaction.atomic():
                # Purchase তৈরি
                purchase = Purchase.objects.create(
                    supplier_name=supplier_name,
                    created_by=request.user,
                    total_amount=total_amount,
                    shop=shop
                )

                # PurchaseItem তৈরি (প্রোডাক্ট অবজেক্ট পাস করা হয়েছে)
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product_instance,
                    unit_buy_price=unit_buy_price,
                    quantity=quantity,
                    subtotal=total_amount
                )

                # প্রোডাক্ট স্টক ও বায় প্রাইস আপডেট
                product_instance.stock += quantity
                product_instance.buy_price = unit_buy_price
                product_instance.save()

            return Response({"message": "Transaction created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "Something went wrong while processing transaction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)