from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from portfolios.models import Portfolio, Holding, PortfolioTransaction
from market.models import Stock

@api_view(['POST'])
def create_portfolio(request):
    user = request.user
    data = request.data
    name = data.get('name')
    description = data.get('description', '')
    benchmark_id = data.get('benchmark_id')

    if not name or not benchmark_id:
        return Response({'error': 'name and benchmark_id required'}, status=400)

    portfolio = Portfolio.objects.create(
        user=user,
        name=name,
        description=description,
        benchmark_id=benchmark_id
    )
    return Response({'portfolio_id': portfolio.id, 'name': portfolio.name})

@api_view(['POST'])
def add_holding(request):
    user = request.user
    data = request.data
    portfolio_id = data.get('portfolio_id')
    symbol = data.get('symbol')
    quantity = data.get('quantity')
    avg_buy_price = data.get('avg_buy_price')
    buy_date = data.get('buy_date')
    portfolio = Portfolio.objects.filter(id=portfolio_id, user=user).first()
    stock = Stock.objects.filter(symbol=symbol).first()
    if not portfolio or not stock:
        return Response({'error': 'Invalid portfolio or stock'}, status=400)
    holding = Holding.objects.create(
        portfolio=portfolio,
        stock=stock,
        quantity=quantity,
        avg_buy_price=avg_buy_price,
        buy_date=buy_date
    )
    return Response({'holding_id': holding.id})

@api_view(['POST'])
def add_transaction(request):
    user = request.user
    data = request.data
    portfolio_id = data.get('portfolio_id')
    symbol = data.get('symbol')
    transaction_type = data.get('transaction_type')
    quantity = data.get('quantity')
    price = data.get('price')
    transaction_date = data.get('transaction_date')
    portfolio = Portfolio.objects.filter(id=portfolio_id, user=user).first()
    stock = Stock.objects.filter(symbol=symbol).first()
    if not portfolio or not stock:
        return Response({'error': 'Invalid portfolio or stock'}, status=400)
    tx = PortfolioTransaction.objects.create(
        portfolio=portfolio,
        stock=stock,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        transaction_date=transaction_date
    )
    return Response({'transaction_id': tx.id})
