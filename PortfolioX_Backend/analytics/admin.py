from django.contrib import admin
from .models import AnalysisResult, PortfolioValueHistory

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'analysis_date', 'health_score', 'diversification_score', 'return_ytd', 'alpha']
    list_filter = ['analysis_date', 'portfolio']
    search_fields = ['portfolio__name']
    readonly_fields = ['created_at']

@admin.register(PortfolioValueHistory)
class PortfolioValueHistoryAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'record_date', 'total_value', 'daily_return', 'cumulative_return']
    list_filter = ['record_date', 'portfolio']
    search_fields = ['portfolio__name']
    ordering = ['-record_date']
