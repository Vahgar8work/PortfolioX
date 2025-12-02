import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from analytics.models import PortfolioValueHistory
from . import RISK_FREE_RATE


class RiskMetrics:
    
    @staticmethod
    def calculate_all_metrics(portfolio_id):
        """Calculate all risk metrics"""
        return {
            'volatility_30d': RiskMetrics.calculate_volatility(portfolio_id, 30),
            'max_drawdown': RiskMetrics.calculate_max_drawdown(portfolio_id),
            'var_95': RiskMetrics.calculate_var(portfolio_id),
            'sharpe_ratio': RiskMetrics.calculate_sharpe_ratio(portfolio_id),
        }
    
    @staticmethod
    def calculate_volatility(portfolio_id, days=30):
        """Calculate portfolio volatility (annualized)"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date
            ).order_by('record_date').values_list('daily_return', flat=True)
            
            returns = [float(r) for r in history if r is not None]
            
            if len(returns) < 10:
                return None
            
            volatility = np.std(returns) * np.sqrt(252)
            return round(volatility, 2)
        
        except Exception:
            return None
    
    @staticmethod
    def calculate_max_drawdown(portfolio_id):
        """Calculate maximum drawdown"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date
            ).order_by('record_date').values_list('total_value', flat=True)
            
            values = [float(v) for v in history]
            
            if len(values) < 10:
                return None
            
            cumulative = np.array(values)
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max * 100
            max_dd = drawdown.min()
            
            return round(max_dd, 2)
        
        except Exception:
            return None
    
    @staticmethod
    def calculate_var(portfolio_id, confidence=0.95):
        """Calculate Value at Risk at 95 percent confidence"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
            
            history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date
            ).order_by('record_date')
            
            returns = [float(h.daily_return) for h in history if h.daily_return is not None]
            
            if len(returns) < 30:
                return None
            
            var = np.percentile(returns, (1 - confidence) * 100)
            current_value = float(history.last().total_value)
            var_amount = var * current_value / 100
            
            return round(var_amount, 2)
        
        except Exception:
            return None
    
    @staticmethod
    def calculate_sharpe_ratio(portfolio_id):
        """Calculate Sharpe Ratio (annualized)"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date
            ).order_by('record_date')
            
            if history.count() < 2:
                return None
            
            start_value = float(history.first().total_value)
            end_value = float(history.last().total_value)
            
            if start_value == 0:
                return None
            
            annual_return = ((end_value - start_value) / start_value)
            
            returns = [float(h.daily_return) / 100 for h in history if h.daily_return is not None]
            
            if len(returns) < 30:
                return None
            
            volatility = np.std(returns) * np.sqrt(252)
            
            if volatility == 0:
                return None
            
            sharpe = (annual_return - RISK_FREE_RATE) / volatility
            
            return round(sharpe, 3)
        
        except Exception:
            return None
