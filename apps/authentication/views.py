from django.core.checks import mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import User
from apps.shops.models import Shop

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                access_token = RefreshToken.for_user(user).access_token
                shop = Shop.objects.filter(owner=user).first()
                if shop:
                    return Response({'message': 'Login successful', 'user': user.email, 'shop': shop.name, 'access_token': str(access_token)}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Login successful', 'user': user.email, 'shop': False, 'access_token': str(access_token)}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        role = request.data.get('role', 'SHOP_OWNER')  # Default role is SHOP_OWNER

        if not email or not password or not phone or not first_name or not last_name:
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if not username:
            return Response({'message': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        if username and User.objects.filter(username=username).exists():
            return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role=role
        )

        return Response({'message': 'User registered successfully', 'user': user.email}, status=status.HTTP_201_CREATED)
        