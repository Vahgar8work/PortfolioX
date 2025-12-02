from celery import shared_task
from portfolios.models import Portfolio
from analytics.services.analyzer import PortfolioAnalyzer
from analytics.services.returns_calculator import ReturnsCalculator
from analytics.services.alert_generator import AlertGenerator
from analytics.models import AnalysisResult, PortfolioValueHistory
from datetime import datetime, timedelta


@shared_task
def run_daily_analysis():
    """Run analysis for all active portfolios (scheduled nightly)"""
    portfolios = Portfolio.objects.filter(is_active=True)
    
    results = {
        'total': portfolios.count(),
        'success': 0,
        'failed': 0,
    }
    
    for portfolio in portfolios:
        try:
            PortfolioAnalyzer.analyze_portfolio(portfolio.id)
            results['success'] += 1
        except Exception as e:
            print(f"Failed to analyze portfolio {portfolio.id}: {e}")
            results['failed'] += 1
    
    return results


@shared_task
def analyze_single_portfolio(portfolio_id):
    """Analyze a single portfolio (can be called manually or via API)"""
    try:
        result = PortfolioAnalyzer.analyze_portfolio(portfolio_id)
        return {'status': 'success', 'portfolio_id': portfolio_id}
    except Exception as e:
        return {'status': 'failed', 'portfolio_id': portfolio_id, 'error': str(e)}


@shared_task
def update_portfolio_values():
    """Update current portfolio values based on latest stock prices"""
    from portfolios.models import Holding
    
    portfolios = Portfolio.objects.filter(is_active=True)
    
    for portfolio in portfolios:
        holdings = Holding.objects.filter(portfolio=portfolio).select_related('stock')
        
        total_invested = 0
        total_current = 0
        
        for holding in holdings:
            if holding.stock.current_price:
                holding.current_value = float(holding.quantity) * float(holding.stock.current_price)
                holding.invested_value = float(holding.quantity) * float(holding.avg_buy_price)
                holding.gain_loss = holding.current_value - holding.invested_value
                holding.save()
                
                total_invested += holding.invested_value
                total_current += holding.current_value
        
        portfolio.total_invested = total_invested
        portfolio.current_value = total_current
        portfolio.total_gain_loss = total_current - total_invested
        if total_invested > 0:
            portfolio.total_gain_pct = (portfolio.total_gain_loss / total_invested) * 100
        portfolio.save()
        
        PortfolioValueHistory.objects.create(
            portfolio=portfolio,
            record_date=datetime.now().date(),
            total_value=total_current,
            invested_value=total_invested
        )
        
        ReturnsCalculator.update_daily_returns(portfolio.id)


@shared_task
def generate_alerts_for_portfolio(portfolio_id):
    """Generate alerts based on latest analysis"""
    try:
        analysis = AnalysisResult.objects.filter(
            portfolio_id=portfolio_id
        ).order_by('-analysis_date').first()
        
        if not analysis:
            return {'status': 'no_analysis'}
        
        portfolio = Portfolio.objects.get(id=portfolio_id)
        recommendations = analysis.recommendations
        
        alerts = AlertGenerator.generate_alerts(
            user_id=portfolio.user_id,
            portfolio_id=portfolio_id,
            recommendations=recommendations
        )
        
        return {
            'status': 'success',
            'alerts_created': len(alerts)
        }
    
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}


@shared_task
def daily_batch_job():
    """Main daily batch job - runs everything in sequence"""
    results = {}
    
    results['update_values'] = update_portfolio_values()
    results['analysis'] = run_daily_analysis()
    
    portfolios = Portfolio.objects.filter(is_active=True)
    alerts_count = 0
    for portfolio in portfolios:
        result = generate_alerts_for_portfolio(portfolio.id)
        if result.get('status') == 'success':
            alerts_count += result.get('alerts_created', 0)
    
    results['alerts_generated'] = alerts_count
    
    return results
