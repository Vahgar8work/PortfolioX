from django.db import models
from portfolios.models import Portfolio

class AnalysisResult(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    analysis_date = models.DateField()
    
    # CORE SCORES
    health_score = models.IntegerField()
    diversification_score = models.IntegerField()
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    
    # RETURNS (All periods)
    return_1d = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_1w = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_1m = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_3m = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_6m = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_1y = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_ytd = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    
    # BENCHMARK COMPARISON
    benchmark_return_1d = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    benchmark_return_1w = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    benchmark_return_1m = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    benchmark_return_3m = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    benchmark_return_6m = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    benchmark_return_1y = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    benchmark_return_ytd = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    alpha = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    beta = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    
    # ALLOCATION DATA (JSON)
    sector_allocation = models.JSONField(default=dict)
    top_holdings = models.JSONField(default=list)
    concentration_data = models.JSONField(default=dict)
    
    # RISK METRICS
    volatility_30d = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    max_drawdown = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    var_95 = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    
    # RECOMMENDATIONS
    recommendations = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['portfolio', 'analysis_date']
        indexes = [
            models.Index(fields=['portfolio', '-analysis_date'], name='idx_analysis_pf_date'),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.analysis_date}"


class PortfolioValueHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    record_date = models.DateField()
    total_value = models.DecimalField(max_digits=14, decimal_places=2)
    invested_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    daily_return = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    cumulative_return = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    
    class Meta:
        unique_together = ['portfolio', 'record_date']
        indexes = [
            models.Index(fields=['portfolio', '-record_date'], name='idx_pf_value_history'),
        ]
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.record_date}: Rs{self.total_value}"
