from .diversification import DiversificationScorer
from .risk_metrics import RiskMetrics


class HealthCalculator:
    
    @staticmethod
    def calculate_health_score(portfolio_id, analysis_data):
        """Calculate overall portfolio health score (0-100)"""
        
        if not analysis_data or not isinstance(analysis_data, dict):
            return 50
        
        diversification_score = analysis_data.get('diversification_score', 50)
        risk_score = HealthCalculator._risk_score(analysis_data)
        performance_score = HealthCalculator._performance_score(analysis_data)
        
        health_score = (
            diversification_score * 0.35 +
            performance_score * 0.40 +
            risk_score * 0.25
        )
        
        return round(max(0, min(100, health_score)))
    
    @staticmethod
    def _risk_score(analysis_data):
        """Score based on risk metrics (lower risk = higher score)"""
        sharpe = analysis_data.get('sharpe_ratio')
        volatility = analysis_data.get('volatility_30d')
        
        score = 50
        
        if sharpe:
            if sharpe > 2:
                score += 30
            elif sharpe > 1.5:
                score += 20
            elif sharpe > 1:
                score += 10
            elif sharpe < 0.5:
                score -= 20
        
        if volatility:
            if volatility < 15:
                score += 20
            elif volatility < 20:
                score += 10
            elif volatility > 30:
                score -= 20
            elif volatility > 25:
                score -= 10
        
        return max(0, min(100, score))
    
    @staticmethod
    def _performance_score(analysis_data):
        """Score based on returns and alpha"""
        return_ytd = analysis_data.get('return_ytd', 0)
        alpha = analysis_data.get('alpha')
        
        score = 50
        
        if return_ytd:
            if return_ytd > 20:
                score += 30
            elif return_ytd > 15:
                score += 20
            elif return_ytd > 10:
                score += 10
            elif return_ytd < 0:
                score -= 20
            elif return_ytd < 5:
                score -= 10
        
        if alpha:
            if alpha > 5:
                score += 20
            elif alpha > 2:
                score += 10
            elif alpha < -5:
                score -= 20
            elif alpha < -2:
                score -= 10
        
        return max(0, min(100, score))
