from portfolios.models import Holding


class RecommendationEngine:
    
    @staticmethod
    def generate_recommendations(portfolio_id, analysis_data):
        """Generate personalized recommendations"""
        recommendations = []
        
        concentration_recs = RecommendationEngine._check_concentration(portfolio_id, analysis_data)
        recommendations.extend(concentration_recs)
        
        div_recs = RecommendationEngine._check_diversification(analysis_data)
        recommendations.extend(div_recs)
        
        perf_recs = RecommendationEngine._check_performance(analysis_data)
        recommendations.extend(perf_recs)
        
        risk_recs = RecommendationEngine._check_risk(analysis_data)
        recommendations.extend(risk_recs)
        
        return recommendations
    
    @staticmethod
    def _check_concentration(portfolio_id, analysis_data):
        """Check for concentration risks"""
        recommendations = []
        concentration = analysis_data.get('concentration_data', {})
        
        top_1 = concentration.get('top_1_weight', 0)
        top_5 = concentration.get('top_5_weight', 0)
        
        if top_1 > 25:
            top_holding = analysis_data.get('top_holdings', [{}])[0]
            recommendations.append({
                'type': 'concentration_risk',
                'priority': 'high',
                'message': f"{top_holding.get('symbol', 'Top stock')} is {top_1:.1f}% of your portfolio. Consider reducing exposure.",
                'action': 'REDUCE'
            })
        
        if top_5 > 70:
            recommendations.append({
                'type': 'concentration_risk',
                'priority': 'high',
                'message': f"Top 5 holdings represent {top_5:.1f}% of portfolio. Diversify to reduce risk.",
                'action': 'DIVERSIFY'
            })
        
        return recommendations
    
    @staticmethod
    def _check_diversification(analysis_data):
        """Check diversification"""
        recommendations = []
        div_score = analysis_data.get('diversification_score', 50)
        sector_allocation = analysis_data.get('sector_allocation', {})
        
        if div_score < 50:
            recommendations.append({
                'type': 'low_diversification',
                'priority': 'medium',
                'message': f"Diversification score is low ({div_score}/100). Add more stocks from different sectors.",
                'action': 'DIVERSIFY'
            })
        
        for sector, weight in sector_allocation.items():
            if weight > 40:
                recommendations.append({
                    'type': 'sector_imbalance',
                    'priority': 'high',
                    'message': f"{sector} sector is overweight at {weight:.1f}%. Consider rebalancing.",
                    'action': 'REBALANCE'
                })
        
        return recommendations
    
    @staticmethod
    def _check_performance(analysis_data):
        """Check performance metrics"""
        recommendations = []
        alpha = analysis_data.get('alpha')
        return_ytd = analysis_data.get('return_ytd')
        
        if alpha and alpha < -5:
            recommendations.append({
                'type': 'underperformance',
                'priority': 'high',
                'message': f"Portfolio underperforming benchmark by {abs(alpha):.1f}%. Review holdings and consider changes.",
                'action': 'REVIEW'
            })
        
        if return_ytd and return_ytd < 0:
            recommendations.append({
                'type': 'negative_returns',
                'priority': 'medium',
                'message': f"YTD return is {return_ytd:.1f}%. Consider reviewing underperforming stocks.",
                'action': 'REVIEW'
            })
        
        return recommendations
    
    @staticmethod
    def _check_risk(analysis_data):
        """Check risk levels"""
        recommendations = []
        volatility = analysis_data.get('volatility_30d')
        sharpe = analysis_data.get('sharpe_ratio')
        
        if volatility and volatility > 30:
            recommendations.append({
                'type': 'high_volatility',
                'priority': 'medium',
                'message': f"Portfolio volatility is high at {volatility:.1f}%. Consider adding stable, low-beta stocks.",
                'action': 'REDUCE_RISK'
            })
        
        if sharpe and sharpe < 0.5:
            recommendations.append({
                'type': 'poor_risk_return',
                'priority': 'medium',
                'message': f"Risk-adjusted returns are low (Sharpe: {sharpe:.2f}). Portfolio may not be compensating for risk.",
                'action': 'OPTIMIZE'
            })
        
        return recommendations
