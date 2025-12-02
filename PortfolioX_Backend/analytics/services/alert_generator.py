from core.models import Alert


class AlertGenerator:
    
    @staticmethod
    def generate_alerts(user_id, portfolio_id, recommendations):
        """Generate alerts from recommendations"""
        alerts_created = []
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            
            if priority in ['high', 'medium']:
                alert = Alert.objects.create(
                    user_id=user_id,
                    portfolio_id=portfolio_id,
                    alert_type=rec.get('type', 'general'),
                    priority=priority,
                    title=AlertGenerator._get_title(rec['type']),
                    message=rec.get('message', ''),
                    metadata={'action': rec.get('action')}
                )
                alerts_created.append(alert)
        
        return alerts_created
    
    @staticmethod
    def _get_title(alert_type):
        """Get alert title based on type"""
        titles = {
            'concentration_risk': 'Concentration Risk Detected',
            'sector_imbalance': 'Sector Imbalance',
            'underperformance': 'Portfolio Underperformance',
            'high_volatility': 'High Volatility Alert',
            'low_diversification': 'Diversification Needed',
            'negative_returns': 'Negative Returns',
            'poor_risk_return': 'Risk-Return Imbalance',
        }
        return titles.get(alert_type, 'Portfolio Alert')
