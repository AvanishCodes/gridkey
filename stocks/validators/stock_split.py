from rest_framework import serializers


class StockSplitValidator(serializers.Serializer):
    company = serializers.IntegerField()
    split_ratio = serializers.FloatField()
