from django.core.management.base import BaseCommand
from market.utils import load_benchmark_index

BENCHMARKS = [
    # (Yahoo symbol, Custom name, Description)
    ('^NSEI', 'NIFTY 50', 'NSE Nifty 50 Index'),
    ('^BSESN', 'SENSEX', 'BSE Sensex Index'),
    # Add more as needed: Bank Nifty, etc.
]

class Command(BaseCommand):
    help = "Load benchmark indices and their price history from Yahoo Finance"

    def handle(self, *args, **options):
        for symbol, name, description in BENCHMARKS:
            self.stdout.write(f"Loading {symbol} ({name}) ...")
            index = load_benchmark_index(symbol, name, description)
            self.stdout.write(f"  Added/updated: {index.name}")
        self.stdout.write("All benchmarks processed.")
