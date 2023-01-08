from django.urls import re_path
from . import views

urlpatterns = [
    re_path("company/", views.CompanyView.as_view(), name="company"),
    re_path("trade/", views.TradeView.as_view(), name="trade"),
    re_path("stock-split/", views.StockSplitView.as_view(), name="stock-split"),
    re_path("transaction/", views.TransactionDetailsView.as_view(), name="transaction"),
]
