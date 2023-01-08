from stocks.models import Trade, Company
import traceback
from django.db.models import Sum


def create_trade(trade_data: dict) -> Trade | dict:
    """Create a trade."""
    try:
        company_id = trade_data.get("company")
        timestamp = trade_data.get("timestamp", None)
        trade_type = trade_data.get("trade_type", None)
        qty = trade_data.get("qty", 0)
        price = trade_data.get("price", 0)
        amount = qty * price
        total_exit = trade_data.get("total_exit", None)
        # Handle the case where the trade type is not valid
        if trade_type not in ["B", "S"]:
            return {"error": "Invalid trade type"}
        # Handle the case where qty or price is negative or ZERO
        if qty <= 0 or price <= 0:
            return {"error": "Quantity or price cannot be negative"}
        # Create the Trade
        if Company.objects.filter(id=company_id).exists():
            company = Company.objects.get(id=company_id)
            if trade_type == "B":
                if company.remaining_stocks >= qty:
                    company.remaining_stocks -= qty
                    trade = Trade.objects.create(
                        company=company,
                        timestamp=timestamp,
                        trade_type=trade_type,
                        qty=qty,
                        outstanding_qty=qty,
                        price=price,
                        outstanding_amount=amount,
                        amount=amount,
                        total_exit=total_exit,
                    )
                    # Get the total outstanding qty of the company
                    trade.save()
                    outstanding_buys = Trade.objects.filter(
                        company=company, trade_type="B", outstanding_qty__gt=0
                    )
                    total_outstanding_amount = 0
                    total_outstanding_qty = outstanding_buys.aggregate(
                        Sum("outstanding_qty")
                    )["outstanding_qty__sum"]
                    for outstanding_buy in outstanding_buys:
                        total_outstanding_amount += (
                            outstanding_buy.outstanding_qty * outstanding_buy.price
                        )
                    # Get the average stock price
                    company.average_stock_price = (
                        total_outstanding_amount / total_outstanding_qty
                    )
                    trade.avg_buy_price = company.average_stock_price
                    trade.save()
                    company.save()
                    # If there exist trades of BUY oper
                    return trade
                else:
                    {"error": "Not enough stocks to buy"}
            if trade_type == "S":
                if company.remaining_stocks + qty > company.total_stocks:
                    return {"error": "Not enough stocks to sell"}
                company.remaining_stocks += qty
                trade = Trade.objects.create(
                    company=company,
                    timestamp=timestamp,
                    trade_type=trade_type,
                    qty=qty,
                    outstanding_qty=0,
                    price=price,
                    outstanding_amount=0,
                    amount=amount,
                    total_exit=total_exit,
                )
                trade.save()
                # Reduce the stocks from buy trades in FIFO order
                buy_trades = Trade.objects.filter(
                    company=company, trade_type="B", outstanding_qty__gt=0
                ).order_by("timestamp")
                for buy_trade in buy_trades:
                    if buy_trade.outstanding_qty >= qty:
                        buy_trade.outstanding_qty -= qty
                        buy_trade.outstanding_amount = (
                            buy_trade.outstanding_qty * buy_trade.price
                        )
                        buy_trade.save()
                        break
                    else:
                        qty -= buy_trade.outstanding_qty
                        buy_trade.outstanding_qty = 0
                        buy_trade.outstanding_amount = 0
                        buy_trade.save()
                # Get the total outstanding qty of the company
                outstanding_buys = Trade.objects.filter(
                    company=company, trade_type="B", outstanding_qty__gt=0
                )
                total_outstanding_amount = 0
                total_outstanding_qty = outstanding_buys.aggregate(
                    Sum("outstanding_qty")
                )["outstanding_qty__sum"]
                for outstanding_buy in outstanding_buys:
                    total_outstanding_amount += (
                        outstanding_buy.outstanding_qty * outstanding_buy.price
                    )
                # Get the average stock price
                if total_outstanding_qty:
                    company.average_stock_price = (
                        total_outstanding_amount / total_outstanding_qty
                    )
                trade.avg_buy_price = company.average_stock_price
                trade.save()
                company.save()
                return trade
        return {
            "error": "Company does not exist",
        }
    except:
        traceback.print_exc()
        return {
            "message": "Error creating trade",
        }
