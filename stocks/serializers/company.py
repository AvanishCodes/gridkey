from rest_framework.serializers import ModelSerializer
from stocks.models import Company


class CompanySerializer(ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "symbol",
            "remaining_stocks",
            "average_stock_price",
            "total_stocks",
        )
