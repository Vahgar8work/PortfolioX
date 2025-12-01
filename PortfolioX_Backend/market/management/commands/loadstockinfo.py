from django.core.management.base import BaseCommand, CommandError
from market.utils import search_yahoo_stock
from market.models import Stock, StockPriceHistory
import yfinance as yf

class Command(BaseCommand):
    help = "Search stocks on Yahoo Finance by partial name or symbol and load to DB"

    def add_arguments(self, parser):
        parser.add_argument('partial_name', type=str)

    def handle(self, *args, **options):
        partial = options['partial_name']
        results = search_yahoo_stock(partial)
        if not results:
            self.stdout.write("No matching stock found.")
            return
        self.stdout.write("Search results:")
        for idx, res in enumerate(results):
            self.stdout.write(f"{idx+1}. {res['symbol']} - {res['name']} ({res['exchange']})")
        selected = int(input("Enter the number to load this stock: ")) - 1
        choose = results[selected]
        ticker = yf.Ticker(choose['symbol'])
        info = ticker.info
        stock, created = Stock.objects.update_or_create(
            symbol=choose['symbol'],
            defaults={
                'name': choose['name'],
                'exchange': choose['exchange'],
                'current_price': info.get('currentPrice'),
                'previous_close': info.get('previousClose'),
                'day_change': info.get('currentPrice', 0) - info.get('previousClose', 0),
                'day_change_pct': info.get('regularMarketChangePercent', 0),
                'is_active': True,
            }
        )
        hist = ticker.history(period="90d")
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
        self.stdout.write(f"Added/updated {stock.name} ({stock.symbol}) with recent price history.")
