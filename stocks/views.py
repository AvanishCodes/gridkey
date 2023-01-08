from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services.stock_split import perform_stock_split

from .services.trade import create_trade
from .validators import (
    TradeCreateValidator,
    CompanyCreateValidator,
    StockSplitValidator,
)
from .models import Company, Trade
from .serializers import CompanySerializer, TradeSerializer

# Create your views here.


class CompanyView(APIView):
    symbol = openapi.Parameter(
        "symbol",
        openapi.IN_QUERY,
        description="Company Symbol",
        type=openapi.TYPE_STRING,
    )
    name = openapi.Parameter(
        "name", openapi.IN_QUERY, description="Company Name", type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[symbol, name])
    def get(self, request, *args, **kwargs):
        symbol = request.GET.get("symbol", "")
        name = request.GET.get("name", "")
        companies = list()
        error = None
        if not (symbol or name):
            return Response(
                {"error": "Please provide either symbol or name"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if symbol:
            companies = Company.objects.filter(symbol=symbol)
        elif name:
            companies = Company.objects.filter(name=name)
        if companies:
            companies = CompanySerializer(companies, many=True).data
        else:
            error = "No companies found"
        return Response(
            {
                "message": "Companies fetched successfully",
                "companies": companies,
                "error": error,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(request_body=CompanyCreateValidator)
    def post(self, request, *args, **kwargs):
        if (
            Company.objects.filter(symbol=request.data["symbol"]).exists()
            or Company.objects.filter(name=request.data["name"]).exists()
        ):
            return Response(
                {"error": "Company with this symbol or name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        data["remaining_stocks"] = data["total_stocks"]
        company = Company.objects.create(**data)
        company = CompanySerializer(company).data
        return Response(
            {"message": "Company created successfully", "company": company},
            status=status.HTTP_200_OK,
        )


class TradeView(APIView):
    company_id = openapi.Parameter(
        "company",
        openapi.IN_QUERY,
        description="Company ID",
        type=openapi.TYPE_INTEGER,
    )
    company_symbol = openapi.Parameter(
        "company_symbol",
        openapi.IN_QUERY,
        description="Company Symbol",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[company_id, company_symbol])
    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("company", "")
        company_symbol = request.GET.get("company_symbol", "")
        trades = list()
        if company_id:
            trades = Trade.objects.filter(company=company_id)
        elif company_symbol:
            company = Company.objects.get(symbol=company_symbol)
            trades = Trade.objects.filter(company=company.id)
        if trades:
            trades = TradeSerializer(trades, many=True).data
        return Response(
            {"message": "Trades fetched successfully", "trades": trades},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(request_body=TradeCreateValidator)
    def post(self, request, *args, **kwargs):
        trade = create_trade(request.data)
        if isinstance(trade, Trade):
            trade = TradeSerializer(trade).data
            return Response(
                {"message": "Trade created successfully", "trade": trade},
                status=status.HTTP_200_OK,
            )
        return Response(trade, status=status.HTTP_400_BAD_REQUEST)


class StockSplitView(APIView):
    @swagger_auto_schema(request_body=StockSplitValidator)
    def post(self, request, *args, **kwargs):
        company_id = request.data.get("company", "")
        split_ratio = request.data.get("split_ratio", 0)
        if Company.objects.filter(id=company_id).exists() and split_ratio > 1:
            res = perform_stock_split(company_id, split_ratio)
            if res:
                return Response(res, status=status.HTTP_200_OK)
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"message": "Company ID and/or split ratio are not correct"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class TransactionDetailsView(APIView):
    company_id = openapi.Parameter(
        "company",
        openapi.IN_QUERY,
        description="Company ID",
        type=openapi.TYPE_INTEGER,
    )
    company_symbol = openapi.Parameter(
        "company_symbol",
        openapi.IN_QUERY,
        description="Company Symbol",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[company_id, company_symbol])
    def get(self, request, *args, **kwargs):
        company_id = request.GET.get("company", "")
        company_symbol = request.GET.get("company_symbol", "")
        if company_id:
            company = Company.objects.get(id=company_id)
        elif company_symbol:
            company = Company.objects.get(symbol=company_symbol)
        else:
            return Response(
                {"message": "Please provide company ID or symbol"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        trades = Trade.objects.filter(company=company.id)
        if trades:
            trades = TradeSerializer(trades, many=True).data
        else:
            trades = []
        return render(
            request,
            "transaction_details.html",
            {"company": company, "trades": trades},
        )
