import numpy as np
from datetime import datetime, timedelta
from analytics.models import PortfolioValueHistory
from market.models import BenchmarkPriceHistory
from . import RISK_FREE_RATE


class AlphaBetaCalculator:
    
    @staticmethod
    def calculate(portfolio_id, benchmark_id, days=365):
        """Calculate alpha and beta"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            pf_history = PortfolioValueHistory.objects.filter(
                portfolio_id=portfolio_id,
                record_date__gte=start_date
            ).order_by('record_date')
            
            bm_history = BenchmarkPriceHistory.objects.filter(
                benchmark_id=benchmark_id,
                trade_date__gte=start_date
            ).order_by('trade_date')
            
            if pf_history.count() < 30 or bm_history.count() < 30:
                return None, None
            
            pf_returns = []
            bm_returns = []
            
            pf_dict = {h.record_date: float(h.daily_return or 0) for h in pf_history if h.daily_return}
            
            bm_values = list(bm_history.values('trade_date', 'close_value'))
            bm_dict = {}
            for i in range(1, len(bm_values)):
                date = bm_values[i]['trade_date']
                close = float(bm_values[i]['close_value'])
                prev_close = float(bm_values[i-1]['close_value'])
                if prev_close and prev_close != 0:
                    daily_ret = ((close - prev_close) / prev_close) * 100
                    bm_dict[date] = daily_ret
            
            common_dates = set(pf_dict.keys()) & set(bm_dict.keys())
            
            for date in sorted(common_dates):
                pf_returns.append(pf_dict[date])
                bm_returns.append(bm_dict[date])
            
            if len(pf_returns) < 30:
                return None, None
            
            covariance = np.cov(pf_returns, bm_returns)[0][1]
            benchmark_variance = np.var(bm_returns)
            
            if benchmark_variance == 0:
                beta = None
            else:
                beta = covariance / benchmark_variance
            
            pf_mean = np.mean(pf_returns) * 252
            bm_mean = np.mean(bm_returns) * 252
            
            if beta is not None:
                alpha = pf_mean - (RISK_FREE_RATE + beta * (bm_mean - RISK_FREE_RATE))
            else:
                alpha = None
            
            return (round(alpha, 2) if alpha else None), (round(beta, 3) if beta else None)
        
        except Exception as e:
            print(f"Error calculating alpha/beta: {e}")
            return None, None
