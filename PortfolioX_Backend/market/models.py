from django.db import models

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    EXCHANGE_CHOICES = [('NSE', 'NSE'), ('BSE', 'BSE')]
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    exchange = models.CharField(max_length=10, choices=EXCHANGE_CHOICES, default='NSE')
    isin = models.CharField(max_length=12, null=True, blank=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    previous_close = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    day_change = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    day_change_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['symbol'], name='idx_stocks_symbol'),
            models.Index(fields=['sector'], name='idx_stocks_sector'),
        ]
class StockPriceHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    trade_date = models.DateField()
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField(null=True)
    daily_return = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['stock', 'trade_date']
        indexes = [
            models.Index(fields=['stock', '-trade_date'], name='idx_price_history_stock_date'),
            models.Index(fields=['trade_date'], name='idx_price_history_date'),
        ]
class BenchmarkIndex(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    last_updated = models.DateTimeField(null=True)
class BenchmarkPriceHistory(models.Model):
    benchmark = models.ForeignKey(BenchmarkIndex, on_delete=models.CASCADE)
    trade_date = models.DateField()
    close_value = models.DecimalField(max_digits=12, decimal_places=2)
    daily_return = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    class Meta:
        unique_together = ['benchmark', 'trade_date']
