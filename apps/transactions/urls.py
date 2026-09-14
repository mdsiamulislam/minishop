from django.urls import path

from apps.transactions import views

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='transaction-list'),

    path('sales/', views.SaleTransactionView.as_view(), name='sale-list'),

    path('summary/', views.TransactionSummaryView.as_view(),name='sale-detail'),
]
