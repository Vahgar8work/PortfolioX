from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from market.models import Stock, StockPriceHistory
from market.utils import search_yahoo_stock
import yfinance as yf

@api_view(['POST'])
def add_and_populate_stock(request):
    partial_name = request.data.get('partial_name', '').strip()
    if not partial_name:
        return Response({'error': 'partial_name is required'}, status=400)

    stock, created = Stock.objects.get_or_create(symbol=partial_name, defaults={'name': partial_name})
    candidates = search_yahoo_stock(partial_name)
    if not candidates:
        return Response({'error': f'No matching stocks found for {partial_name}'}, status=404)
    selected = candidates[0]
    yf_symbol = selected['symbol']

    ticker = yf.Ticker(yf_symbol)
    info = ticker.info
    stock.name = selected['name']
    stock.symbol = yf_symbol
    stock.exchange = selected['exchange']
    stock.current_price = info.get('currentPrice')
    stock.previous_close = info.get('previousClose')
    stock.day_change = info.get('currentPrice', 0) - info.get('previousClose', 0) if info.get('currentPrice') and info.get('previousClose') else None
    stock.day_change_pct = info.get('regularMarketChangePercent')
    stock.is_active = True
    stock.save()

    hist = ticker.history(period="90d")
    count = 0
    for dt, row in hist.iterrows():
        StockPriceHistory.objects.update_or_create(
            stock=stock,
            trade_date=dt.date(),
            defaults={
                'open_price': row['Open'],
                'high_price': row['High'],
                'low_price': row['Low'],
                'close_price': row['Close'],
                'volume': row['Volume'],
                'daily_return': None,
            }
        )
        count += 1

    return Response({
        'symbol': stock.symbol,
        'name': stock.name,
        'exchange': stock.exchange,
        'current_price': stock.current_price,
        'loaded_history_records': count
    })
