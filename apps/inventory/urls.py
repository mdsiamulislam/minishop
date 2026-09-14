from django.urls import path
from apps.inventory import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryListView.as_view(), name='category-detail'),
    
    path('products/', views.ProductListView.as_view(), name='product-list'),
]
