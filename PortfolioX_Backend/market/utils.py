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
import yfinance as yf

def search_yahoo_stock(partial_name):
    # Returns a list of dicts just like before
    candidates = []
    suffixes = ['.NS', '.BO', '']
    partial = partial_name.upper()
    for suffix in suffixes:
        try:
            symbol = partial + suffix
            ticker = yf.Ticker(symbol)
            info = ticker.info
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

import yfinance as yf
from datetime import datetime
from market.models import BenchmarkIndex, BenchmarkPriceHistory

def load_benchmark_index(yahoo_symbol, custom_name=None, description=None):
    ticker = yf.Ticker(yahoo_symbol)
    info = ticker.info
    # Convert Yahoo "regularMarketTime" to a Python datetime, if it exists
    last_updated = None
    if 'regularMarketTime' in info and info['regularMarketTime']:
        # regularMarketTime is a Unix timestamp (int)
        last_updated = datetime.fromtimestamp(info['regularMarketTime'])
    index, _ = BenchmarkIndex.objects.update_or_create(
        symbol=yahoo_symbol,
        defaults={
            'name': custom_name or info.get('longName', yahoo_symbol),
            'description': description or info.get('longBusinessSummary', ''),
            'current_value': info.get('regularMarketPrice'),
            'last_updated': last_updated,
        }
    )
    # Import price history (keep this section as-is)
    hist = ticker.history(period="90d")
    for dt, row in hist.iterrows():
        BenchmarkPriceHistory.objects.update_or_create(
            benchmark=index,
            trade_date=dt.date(),
            defaults={
                'close_value': row['Close'],
                'daily_return': None if row['Close'] is None else 0.0  # Put logic here if desired
            }
        )
    return index
