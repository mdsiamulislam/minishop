from django.urls import path

from apps.shops import views

urlpatterns = [
    path('', views.ShopListView.as_view(), name='shop-list'),
    path('myshop/', views.ShopView.as_view(), name='show-view')
]
