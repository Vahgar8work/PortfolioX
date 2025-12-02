from datetime import datetime
from portfolios.models import Portfolio
from analytics.models import AnalysisResult
from .returns_calculator import ReturnsCalculator
from .risk_metrics import RiskMetrics
from .diversification import DiversificationScorer
from .alpha_beta import AlphaBetaCalculator
from .health_calculator import HealthCalculator
from .recommender import RecommendationEngine


class PortfolioAnalyzer:
    """Main orchestrator for portfolio analysis"""
    
    @staticmethod
    def analyze_portfolio(portfolio_id):
        """Run complete portfolio analysis"""
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
            
            # 1. Calculate returns
            returns_data = ReturnsCalculator.calculate_portfolio_returns(portfolio_id)
            
            # 2. Calculate benchmark returns
            benchmark_returns = ReturnsCalculator.calculate_benchmark_returns(portfolio.benchmark_id)
            
            # 3. Calculate risk metrics
            risk_data = RiskMetrics.calculate_all_metrics(portfolio_id)
            
            # 4. Calculate diversification
            div_score = DiversificationScorer.calculate_score(portfolio_id)
            sector_allocation = DiversificationScorer.get_sector_allocation(portfolio_id)
            top_holdings = DiversificationScorer.get_top_holdings(portfolio_id)
            concentration = DiversificationScorer.get_concentration_data(portfolio_id)
            
            # 5. Calculate alpha and beta
            alpha, beta = AlphaBetaCalculator.calculate(portfolio_id, portfolio.benchmark_id)
            
            # 6. Combine all data
            analysis_data = {
                **returns_data,
                **benchmark_returns,
                **risk_data,
                'diversification_score': div_score,
                'sector_allocation': sector_allocation,
                'top_holdings': top_holdings,
                'concentration_data': concentration,
                'alpha': alpha,
                'beta': beta,
            }
            
            # 7. Calculate health score
            health_score = HealthCalculator.calculate_health_score(portfolio_id, analysis_data)
            analysis_data['health_score'] = health_score
            
            # 8. Generate recommendations
            recommendations = RecommendationEngine.generate_recommendations(portfolio_id, analysis_data)
            analysis_data['recommendations'] = recommendations
            
            # 9. Save to database
            analysis_result = AnalysisResult.objects.update_or_create(
                portfolio_id=portfolio_id,
                analysis_date=datetime.now().date(),
                defaults=analysis_data
            )
            
            return analysis_data
        
        except Exception as e:
            print(f"Error analyzing portfolio {portfolio_id}: {e}")
            return None
