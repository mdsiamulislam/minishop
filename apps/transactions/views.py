from decimal import Decimal, InvalidOperation
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import uuid

from apps.transactions.models import Purchase, PurchaseItem, Sale, SaleItem
from apps.inventory.models import Product
from apps.shops.models import Shop


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supplier_name = request.data.get('supplier_name')
        product_id = request.data.get('product')

        # ১. ডাটা টাইপ কনভার্সন ও ভ্যালিডেশন (Decimal ব্যবহার করা নিরাপদ)
        try:
            quantity = int(request.data.get('quantity', 0))
            unit_buy_price = Decimal(str(request.data.get('unit_buy_price', 0)))
        except (ValueError, TypeError, InvalidOperation):
            return Response(
                {"error": "Quantity and unit_buy_price must be valid numbers."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

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

        # ৪. Atomic Transaction
        try:
            with transaction.atomic():
                # Purchase তৈরি
                purchase = Purchase.objects.create(
                    supplier_name=supplier_name,
                    created_by=request.user,
                    total_amount=total_amount,
                    shop=shop
                )

                # PurchaseItem তৈরি
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product_instance,
                    unit_buy_price=unit_buy_price,
                    quantity=quantity,
                    subtotal=total_amount
                )

                # প্রোডাক্ট স্টক ও বায় প্রাইস আপডেট
                product_instance.stock += quantity
                product_instance.buy_price = unit_buy_price
                product_instance.save()

            return Response({"message": "Purchase transaction created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": "Something went wrong while processing purchase."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaleTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"error": "No shop found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        invoice_no = str(uuid.uuid4()).replace('-', '').upper()[:12]
        customer_name = request.data.get('customer_name')
        product_id = request.data.get('products')

        # ১. সেফলি ডাটা রিড করা (Unchecked/Empty handle করা)
        raw_quantity = request.data.get('quantity')
        raw_discount = request.data.get('discount')
        raw_unit_price = request.data.get('unit_price')

        try:
            quantity = int(raw_quantity) if raw_quantity not in [None, ''] else 0
            discount = Decimal(str(raw_discount)) if raw_discount not in [None, ''] else Decimal('0.00')
        except (ValueError, TypeError, InvalidOperation):
            return Response(
                {"error": "Quantity and discount must be valid numbers."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0 or discount < 0:
            return Response({"error": "Invalid quantity or discount."}, status=status.HTTP_400_BAD_REQUEST)

        # ২. প্রোডাক্ট চেক
        try:
            product_instance = Product.objects.get(id=product_id, shop=shop)
        except Product.DoesNotExist:
            return Response({"error": "Product not found in your shop."}, status=status.HTTP_404_NOT_FOUND)

        # ৩. স্টক চেক
        if product_instance.stock < quantity:
            return Response(
                {"error": f"Insufficient stock! Available: {product_instance.stock}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ৪. unit_price সেফলি হ্যান্ডেল করা
        try:
            if raw_unit_price not in [None, '']:
                unit_price = Decimal(str(raw_unit_price))
            else:
                unit_price = Decimal(str(product_instance.sell_price))
        except (ValueError, TypeError, InvalidOperation):
            return Response({"error": "Invalid unit_price format."}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = quantity * unit_price
        net_amount = total_amount - discount

        if net_amount < 0:
            return Response({"error": "Discount cannot be greater than total amount."}, status=status.HTTP_400_BAD_REQUEST)

        # ৫. Atomic Transaction
        try:
            with transaction.atomic():
                sale = Sale.objects.create(
                    shop=shop,
                    invoice_no=invoice_no,
                    customer_name=customer_name,
                    total_amount=total_amount,
                    discount=discount,
                    net_amount=net_amount,
                    created_by=request.user
                )

                SaleItem.objects.create(
                    sale=sale,
                    product=product_instance,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=total_amount
                )

                # স্টক আপডেট
                product_instance.stock -= quantity
                product_instance.save()

            return Response({"message": "Sale transaction completed successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            # অরিজিনাল এররটি বোঝার সুবিধার্থে প্রিন্ট দিন (Console এ দেখতে পাবেন)
            print("Sale Error:", str(e))
            return Response({"error": f"Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)















class TransactionSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"error": "No shop found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        # ১. শপের সকল Sales এবং Purchases ফিল্টার
        sales = Sale.objects.filter(shop=shop).order_by('-created_at')
        purchases = Purchase.objects.filter(shop=shop).order_by('-created_at')

        # ২. মোট বিক্রয়, ছাড়, ও নেট বিক্রয় হিসাব
        total_sales_amount = sum(sale.total_amount for sale in sales)
        total_discount = sum(sale.discount for sale in sales)
        total_net_sales = sum(sale.net_amount for sale in sales)

        # ৩. মোট ক্রয় খরচ হিসাব
        total_purchase_amount = sum(purchase.total_amount for purchase in purchases)

        # ৪. বিক্রি হওয়া আইটেমগুলোর মোট কেনা দাম (Cost of Goods Sold - COGS) বের করা
        total_cogs = Decimal('0.00')
        sale_items = SaleItem.objects.filter(sale__shop=shop)
        for item in sale_items:
            total_cogs += item.quantity * item.product.buy_price

        # ৫. প্রফিট/লস ক্যালকুলেশন
        # Gross Profit = মোট নেট সেল - বিক্রি হওয়া পণ্যের আসল কেনা দাম
        gross_profit = total_net_sales - total_cogs

        # Net cash balance = মোট কত টাকা পকেটে আসলো/গেল (নেট বিক্রি - মোট নতুন পণ্য ক্রয়)
        cash_flow_balance = total_net_sales - total_purchase_amount

        # ৬. সেলস ট্রানজ্যাকশন লিস্ট প্রসেসিং
        sales_data = []
        for sale in sales:
            items = SaleItem.objects.filter(sale=sale)
            sales_data.append({
                "id": sale.id,
                "invoice_no": sale.invoice_no,
                "customer_name": sale.customer_name,
                "total_amount": sale.total_amount,
                "discount": sale.discount,
                "net_amount": sale.net_amount,
                "created_at": sale.created_at,
                "items": [
                    {
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "subtotal": item.subtotal
                    } for item in items
                ]
            })

        # ৭. পারচেজ ট্রানজ্যাকশন লিস্ট প্রসেসিং
        purchases_data = []
        for purchase in purchases:
            items = PurchaseItem.objects.filter(purchase=purchase)
            purchases_data.append({
                "id": purchase.id,
                "supplier_name": purchase.supplier_name,
                "total_amount": purchase.total_amount,
                "created_at": purchase.created_at,
                "items": [
                    {
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "unit_buy_price": item.unit_buy_price,
                        "subtotal": item.subtotal
                    } for item in items
                ]
            })

        # ৮. ফাইনাল রেসপন্স তৈরি
        response_data = {
            "summary": {
                "total_sales_count": sales.count(),
                "total_purchases_count": purchases.count(),
                "total_sales_amount": total_sales_amount,
                "total_discount_given": total_discount,
                "total_net_sales": total_net_sales,
                "total_purchase_cost": total_purchase_amount,
                "cost_of_goods_sold": total_cogs,
                "gross_profit": gross_profit,  # নেট লাভ/ক্ষতি (বিক্রি হওয়া পণ্যের ওপর)
                "is_profitable": gross_profit >= 0
            },
            "sales_transactions": sales_data,
            "purchase_transactions": purchases_data
        }

        return Response(response_data, status=status.HTTP_200_OK)