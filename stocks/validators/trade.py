from rest_framework import serializers


class TradeCreateValidator(serializers.Serializer):
    company = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    trade_type = serializers.CharField(required=True)
    qty = serializers.FloatField(required=True)
    price = serializers.FloatField(required=True)
    total_exit = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
