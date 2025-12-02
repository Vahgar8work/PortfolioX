from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from portfolios.models import Portfolio
from analytics.models import AnalysisResult
from analytics.services.analyzer import PortfolioAnalyzer
from datetime import datetime, timedelta

User = get_user_model()


@api_view(['GET'])
def get_portfolio_analysis(request, portfolio_id):
    """Get latest analysis for a portfolio"""
    # Temporary: Get first user for testing
    user = User.objects.first()
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    analysis = AnalysisResult.objects.filter(
        portfolio_id=portfolio_id
    ).order_by('-analysis_date').first()
    
    if not analysis:
        return Response({'error': 'No analysis found. Run analysis first.'}, status=404)
    
    return Response({
        'portfolio_id': portfolio.id,
        'portfolio_name': portfolio.name,
        'analysis_date': analysis.analysis_date,
        'health_score': analysis.health_score,
        'diversification_score': analysis.diversification_score,
        'risk_score': float(analysis.risk_score) if analysis.risk_score else None,
        'sharpe_ratio': float(analysis.sharpe_ratio) if analysis.sharpe_ratio else None,
        'returns': {
            '1d': float(analysis.return_1d) if analysis.return_1d else None,
            '1w': float(analysis.return_1w) if analysis.return_1w else None,
            '1m': float(analysis.return_1m) if analysis.return_1m else None,
            '3m': float(analysis.return_3m) if analysis.return_3m else None,
            '6m': float(analysis.return_6m) if analysis.return_6m else None,
            '1y': float(analysis.return_1y) if analysis.return_1y else None,
            'ytd': float(analysis.return_ytd) if analysis.return_ytd else None,
        },
        'benchmark_comparison': {
            'alpha': float(analysis.alpha) if analysis.alpha else None,
            'beta': float(analysis.beta) if analysis.beta else None,
            'benchmark_return_ytd': float(analysis.benchmark_return_ytd) if analysis.benchmark_return_ytd else None,
        },
        'risk_metrics': {
            'volatility_30d': float(analysis.volatility_30d) if analysis.volatility_30d else None,
            'max_drawdown': float(analysis.max_drawdown) if analysis.max_drawdown else None,
            'var_95': float(analysis.var_95) if analysis.var_95 else None,
        },
        'sector_allocation': analysis.sector_allocation,
        'top_holdings': analysis.top_holdings,
        'concentration_data': analysis.concentration_data,
        'recommendations': analysis.recommendations,
    })


@api_view(['POST'])
def run_portfolio_analysis(request, portfolio_id):
    """Trigger analysis for a portfolio"""
    user = User.objects.first()
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    result = PortfolioAnalyzer.analyze_portfolio(portfolio_id)
    
    if result:
        return Response({
            'message': 'Analysis completed successfully',
            'portfolio_id': portfolio_id,
            'analysis_date': datetime.now().date(),
            'health_score': result.get('health_score'),
        })
    else:
        return Response({'error': 'Analysis failed'}, status=500)


@api_view(['GET'])
def get_portfolio_performance(request, portfolio_id):
    """Get historical performance data"""
    user = User.objects.first()
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    period = request.GET.get('period', '1y')
    
    periods_map = {
        '1m': 30,
        '3m': 90,
        '6m': 180,
        '1y': 365,
        'all': 3650
    }
    
    days = periods_map.get(period, 365)
    start_date = datetime.now().date() - timedelta(days=days)
    
    analyses = AnalysisResult.objects.filter(
        portfolio_id=portfolio_id,
        analysis_date__gte=start_date
    ).order_by('analysis_date').values(
        'analysis_date',
        'return_ytd',
        'health_score',
        'diversification_score',
        'sharpe_ratio'
    )
    
    return Response({
        'portfolio_id': portfolio_id,
        'period': period,
        'data': list(analyses)
    })


@api_view(['GET'])
def get_recommendations(request, portfolio_id):
    """Get recommendations for a portfolio"""
    user = User.objects.first()
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    
    analysis = AnalysisResult.objects.filter(
        portfolio_id=portfolio_id
    ).order_by('-analysis_date').first()
    
    if not analysis:
        return Response({'error': 'No analysis found'}, status=404)
    
    return Response({
        'portfolio_id': portfolio_id,
        'analysis_date': analysis.analysis_date,
        'recommendations': analysis.recommendations
    })
