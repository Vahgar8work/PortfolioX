from django.contrib import admin
from .models import Sector, Stock, StockPriceHistory, BenchmarkIndex, BenchmarkPriceHistory

admin.site.register(Sector)
admin.site.register(Stock)
admin.site.register(StockPriceHistory)
admin.site.register(BenchmarkIndex)
admin.site.register(BenchmarkPriceHistory)
