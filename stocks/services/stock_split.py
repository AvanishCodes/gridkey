from stocks.models import Trade, Company
from stocks.serializers import CompanySerializer
from django.db.models import F
import traceback


def perform_stock_split_on_trades(company: Company, split_ratio: float) -> bool:
    """Perform stock split for a company"""
    try:
        # Change all the stocks with an outstanding qty with BUY operation
        Trade.objects.filter(
            company=company, trade_type="B", outstanding_qty__gt=0
        ).update(
            qty=F("qty") * split_ratio,
            outstanding_qty=F("outstanding_qty") * split_ratio,
            price=F("price") / split_ratio,
            outstanding_amount=F("outstanding_amount") / split_ratio,
        )
        return True
    except:
        return False


def perform_stock_split(company_id: int, split_ratio: float) -> dict:
    """Perform stock split for a company.
    This function requires a valid company id and a split ratio greater than 1.
    """
    try:
        company = Company.objects.get(id=company_id)
        company.remaining_stocks *= split_ratio
        company.total_stocks *= split_ratio
        company.average_stock_price /= split_ratio
        if perform_stock_split_on_trades(company, split_ratio):
            company.save()
        else:
            return {
                "error": "Stock split failed",
                "company": CompanySerializer(company).data,
            }
        return {
            "message": "Stock split successful",
            "company": CompanySerializer(company).data,
        }
    except:
        traceback.print_exc()
        return {"error": "Stock split failed"}
