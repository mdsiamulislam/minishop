from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from apps.shops.models import Shop
from apps.shops.serializers import ShopSerializer


class ShopListView(APIView):
    def get(self, request):
        shops = Shop.objects.all()
        shop_data = [{"id": shop.id, "name": shop.name} for shop in shops]
        return Response(shop_data, status=status.HTTP_200_OK)



class ShopView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopSerializer

    def get(self, request):
        user = request.user
        try:
            shop = Shop.objects.get(owner=user)
            serializer = self.serializer_class(shop)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return Response({"error": "Shop not found for this user."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        if Shop.objects.filter(owner=user).exists():
            return Response({"error": "User already has a shop."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        try:
            shop = Shop.objects.get(owner=user)
            serializer = self.serializer_class(shop, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Shop.DoesNotExist:
            return Response({"error": "Shop not found for this user."}, status=status.HTTP_404_NOT_FOUND)