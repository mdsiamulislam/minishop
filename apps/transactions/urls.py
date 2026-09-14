from django.urls import path

from apps.transactions import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction-list'),
]
