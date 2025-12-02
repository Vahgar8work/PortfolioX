import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from portfolios.models import Portfolio, Holding
from market.models import StockPriceHistory, BenchmarkPriceHistory
from analytics.models import PortfolioValueHistory


class ReturnsCalculator:
    
    @staticmethod
    def calculate_portfolio_returns(portfolio_id):
        """Calculate returns for all periods"""
        periods = {
            '1d': 1,
            '1w': 7,
            '1m': 30,
            '3m': 90,
            '6m': 180,
            '1y': 365,
        }
        
        results = {}
        for period_name, days in periods.items():
            returns = ReturnsCalculator._calculate_return(portfolio_id, days)
            results[f'return_{period_name}'] = returns
        
        results['return_ytd'] = ReturnsCalculator._calculate_ytd_return(portfolio_id)
        
        return results
    
    @staticmethod
    def _calculate_return(portfolio_id, days):
        """Calculate return for a specific period"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date,
                record_date__lte=end_date
            ).order_by('record_date')
            
            if history.count() < 2:
                return None
            
            start_value = float(history.first().total_value)
            end_value = float(history.last().total_value)
            
            if start_value == 0:
                return None
            
            return_pct = ((end_value - start_value) / start_value) * 100
            return round(return_pct, 2)
        
        except Exception as e:
            print(f"Error calculating return: {e}")
            return None
    
    @staticmethod
    def _calculate_ytd_return(portfolio_id):
        """Calculate Year-to-Date return"""
        try:
            end_date = datetime.now().date()
            start_date = datetime(end_date.year, 1, 1).date()
            
            history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date,
                record_date__lte=end_date
            ).order_by('record_date')
            
            if history.count() < 2:
                return None
            
            start_value = float(history.first().total_value)
            end_value = float(history.last().total_value)
            
            if start_value == 0:
                return None
            
            return_pct = ((end_value - start_value) / start_value) * 100
            return round(return_pct, 2)
        
        except Exception:
            return None
    
    @staticmethod
    def calculate_benchmark_returns(benchmark_id):
        """Calculate benchmark returns for all periods"""
        periods = {
            '1d': 1,
            '1w': 7,
            '1m': 30,
            '3m': 90,
            '6m': 180,
            '1y': 365,
        }
        
        results = {}
        for period_name, days in periods.items():
            returns = ReturnsCalculator._calculate_benchmark_return(benchmark_id, days)
            results[f'benchmark_return_{period_name}'] = returns
        
        results['benchmark_return_ytd'] = ReturnsCalculator._calculate_benchmark_ytd(benchmark_id)
        
        return results
    
    @staticmethod
    def _calculate_benchmark_return(benchmark_id, days):
        """Calculate benchmark return for specific period"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            history = BenchmarkPriceHistory.objects.filter(
                benchmark_id=benchmark_id,
                trade_date__gte=start_date,
                trade_date__lte=end_date
            ).order_by('trade_date')
            
            if history.count() < 2:
                return None
            
            start_value = float(history.first().close_value)
            end_value = float(history.last().close_value)
            
            if start_value == 0:
                return None
            
            return_pct = ((end_value - start_value) / start_value) * 100
            return round(return_pct, 2)
        
        except Exception:
            return None
    
    @staticmethod
    def _calculate_benchmark_ytd(benchmark_id):
        """Calculate benchmark YTD return"""
        try:
            end_date = datetime.now().date()
            start_date = datetime(end_date.year, 1, 1).date()
            
            history = BenchmarkPriceHistory.objects.filter(
                benchmark_id=benchmark_id,
                trade_date__gte=start_date,
                trade_date__lte=end_date
            ).order_by('trade_date')
            
            if history.count() < 2:
                return None
            
            start_value = float(history.first().close_value)
            end_value = float(history.last().close_value)
            
            if start_value == 0:
                return None
            
            return_pct = ((end_value - start_value) / start_value) * 100
            return round(return_pct, 2)
        
        except Exception:
            return None
    
    @staticmethod
    def update_daily_returns(portfolio_id):
        """Calculate and update daily returns for portfolio value history"""
        history = PortfolioValueHistory.objects.filter(
            portfolio_id=portfolio_id
        ).order_by('record_date')
        
        prev_value = None
        for record in history:
            if prev_value and prev_value != 0:
                daily_return = ((float(record.total_value) - prev_value) / prev_value) * 100
                record.daily_return = round(daily_return, 4)
                record.save(update_fields=['daily_return'])
            prev_value = float(record.total_value)
