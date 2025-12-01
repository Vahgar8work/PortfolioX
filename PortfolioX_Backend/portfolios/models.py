from django.db import models
from django.conf import settings
from market.models import Stock, BenchmarkIndex

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    benchmark = models.ForeignKey(BenchmarkIndex, on_delete=models.SET_NULL, null=True, default=1)
    total_invested = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_gain_loss = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_gain_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    day_change = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    day_change_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['user', 'name']

class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='holdings', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    avg_buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    buy_date = models.DateField(null=True)
    invested_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    gain_loss = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    weight_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['portfolio', 'stock']

class PortfolioTransaction(models.Model):
    TYPE_CHOICES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
