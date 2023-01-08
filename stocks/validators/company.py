from rest_framework import serializers


class CompanyCreateValidator(serializers.Serializer):
    name = serializers.CharField(required=True)
    symbol = serializers.CharField(required=True)
    total_stocks = serializers.IntegerField(required=True)
    remaining_stocks = serializers.IntegerField(required=True)
    average_stock_price = serializers.FloatField(required=True)
