# Set up paths
$marketDir = "market"
$mgmtFolder = Join-Path $marketDir "management"
$cmdsFolder = Join-Path $mgmtFolder "commands"

# Create folders and __init__.py files if missing
if (!(Test-Path $mgmtFolder)) { New-Item -ItemType Directory $mgmtFolder | Out-Null }
if (!(Test-Path $cmdsFolder)) { New-Item -ItemType Directory $cmdsFolder | Out-Null }
Set-Content -Path (Join-Path $mgmtFolder "__init__.py") -Value "" -Encoding UTF8
Set-Content -Path (Join-Path $cmdsFolder "__init__.py") -Value "" -Encoding UTF8

# Create market/utils.py
$utilsCode = @"
import yfinance as yf

def search_yahoo_stock(partial_name):
    # Returns a list of (symbol, name, exchange, summary)
    candidates = []
    # Try major Indian suffixes
    suffixes = ['.NS', '.BO', '']
    partial = partial_name.upper()
    for suffix in suffixes:
        try:
            symbol = partial + suffix
            ticker = yf.Ticker(symbol)
            info = ticker.info
            # If Yahoo returns a company name matching or including the partial, accept as candidate
            if info and (partial in (info.get('shortName', '') + info.get('longName', '')).upper()):
                candidates.append({
                    'symbol': symbol,
                    'name': info.get('longName', info.get('shortName', symbol)),
                    'exchange': info.get('exchange', ''),
                    'summary': info.get('longBusinessSummary', '')
                })
        except Exception:
            continue
    return candidates
"@
Set-Content -Path (Join-Path $marketDir "utils.py") -Value $utilsCode -Encoding UTF8

# Create market/management/commands/loadstockinfo.py
$loadStockInfo = @"
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
"@
Set-Content -Path (Join-Path $cmdsFolder "loadstockinfo.py") -Value $loadStockInfo -Encoding UTF8

# Create market/management/commands/bulk_load_stocks.py
$bulkLoadStocks = @"
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
"@
Set-Content -Path (Join-Path $cmdsFolder "bulk_load_stocks.py") -Value $bulkLoadStocks -Encoding UTF8

Write-Host "Custom Yahoo Finance stock search and bulk-load utilities added."
Write-Host "You can now run: python manage.py loadstockinfo RELI   # (for interactive load)"
Write-Host "Or: python manage.py bulk_load_stocks input_symbols.csv # (for bulk loading from file)"
