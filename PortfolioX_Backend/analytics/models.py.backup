from django.db import models
from portfolios.models import Portfolio

class AnalysisResult(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    analysis_date = models.DateField()
    health_score = models.IntegerField()
    diversification_score = models.IntegerField()
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    return_1d = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_ytd = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    alpha = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    beta = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    sector_allocation = models.JSONField(default=dict)
    top_holdings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['portfolio', 'analysis_date']
        indexes = [
            models.Index(fields=['portfolio', '-analysis_date'], name='idx_analysis_pf_date'),
        ]

class PortfolioValueHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    record_date = models.DateField()
    total_value = models.DecimalField(max_digits=14, decimal_places=2)
    invested_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    class Meta:
        unique_together = ['portfolio', 'record_date']
