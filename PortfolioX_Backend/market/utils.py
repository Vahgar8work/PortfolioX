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
