from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.inventory.models import Product, Category
from apps.inventory.serializers import CategorySerializer, ProductSerializer
from apps.shops.models import Shop

class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        categories = Category.objects.filter(shop=shop)
        serializer = CategorySerializer(categories, many=True)
        if serializer.data:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No categories found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shop=shop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            category = Category.objects.get(pk=pk, shop=shop)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            category = Category.objects.get(pk=pk, shop=shop)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        return Response({"detail": "Category deleted successfully."}, status=status.HTTP_200_OK)




class ProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        products = Product.objects.filter(shop=shop)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(shop=shop)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            product = Product.objects.get(pk=pk, shop=shop)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shop = Shop.objects.filter(owner=request.user).first()
        if not shop:
            return Response({"detail": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            product = Product.objects.get(pk=pk, shop=shop)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_200_OK)