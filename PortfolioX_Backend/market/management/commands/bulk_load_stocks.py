import csv
import yfinance as yf
from django.core.management.base import BaseCommand
from market.utils import search_yahoo_stock
from market.models import Stock, StockPriceHistory

class Command(BaseCommand):
    help = "Bulk load stock info and historical prices based on a list of partial names or symbols in a CSV"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV or TXT file (one partial name/symbol per line)')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                lines = [row[0].strip() for row in reader if row]
        except Exception:
            with open(file_path, 'r') as txtfile:
                lines = [line.strip() for line in txtfile.readlines() if line.strip()]
        self.stdout.write(f"Processing {len(lines)} input names/symbols...")
        for partial in lines:
            candidates = search_yahoo_stock(partial)
            if not candidates:
                self.stdout.write(f"No Yahoo Finance match for '{partial}'")
                continue
            match = candidates[0]
            symbol = match['symbol']
            name = match['name']
            exchange = match['exchange']
            self.stdout.write(f"Adding/Updating: {symbol} ({name}) [{exchange}]")
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                stock, created = Stock.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'name': name,
                        'exchange': exchange,
                        'current_price': info.get('currentPrice'),
                        'previous_close': info.get('previousClose'),
                        'day_change': info.get('currentPrice', 0) - info.get('previousClose', 0),
                        'day_change_pct': info.get('regularMarketChangePercent', 0),
                        'is_active': True,
                    }
                )
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
                self.stdout.write(f"Loaded {count} history records for {symbol}")
            except Exception as e:
                self.stdout.write(f"Failed to load '{symbol}': {str(e)}")
        self.stdout.write("Bulk load complete.")
