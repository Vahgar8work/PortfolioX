from django.contrib import admin
from .models import AnalysisResult, PortfolioValueHistory


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'analysis_date', 'health_score', 'diversification_score', 'return_ytd']
    list_filter = ['analysis_date']
    search_fields = ['portfolio__name']
    ordering = ['-analysis_date']


@admin.register(PortfolioValueHistory)
class PortfolioValueHistoryAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'record_date', 'total_value', 'invested_value']
    list_filter = ['record_date']
    search_fields = ['portfolio__name']
    ordering = ['-record_date']

