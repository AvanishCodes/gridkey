from django.db import models

from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """A company"""

    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    total_stocks = models.IntegerField(default=0)
    remaining_stocks = models.IntegerField(default=0)
    average_stock_price = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.symbol} ({self.name})"


class Trade(models.Model):
    """A trade event"""

    class TradeType(models.TextChoices):
        BUY = "B", _("Buy")
        SELL = "S", _("Sell")

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    trade_type = models.CharField(max_length=1, choices=TradeType.choices)
    price = models.FloatField()
    qty = models.FloatField()
    amount = models.FloatField()
    outstanding_qty = models.FloatField()
    outstanding_amount = models.FloatField()
    avg_buy_price = models.FloatField(null=True, default=None)
    total_exit = models.TextField(null=True, default=None)


class StockSplit(models.Model):
    """A stock split event"""

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    ratio = models.FloatField()
