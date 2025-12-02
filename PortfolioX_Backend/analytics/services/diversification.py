import numpy as np
from portfolios.models import Holding
from market.models import Stock


class DiversificationScorer:
    
    @staticmethod
    def calculate_score(portfolio_id):
        """Calculate diversification score (0-100)"""
        holdings = Holding.objects.filter(portfolio_id=portfolio_id).select_related('stock', 'stock__sector')
        
        if holdings.count() == 0:
            return 0
        
        total_value = sum(float(h.current_value or 0) for h in holdings)
        
        if total_value == 0:
            return 0
        
        stock_score = DiversificationScorer._stock_concentration_score(holdings, total_value)
        sector_score = DiversificationScorer._sector_diversification_score(holdings, total_value)
        count_score = DiversificationScorer._holdings_count_score(holdings.count())
        
        final_score = (stock_score * 0.4) + (sector_score * 0.4) + (count_score * 0.2)
        
        return round(final_score)
    
    @staticmethod
    def _stock_concentration_score(holdings, total_value):
        """Penalize high concentration in individual stocks"""
        weights = []
        for h in holdings:
            weight = (float(h.current_value or 0) / total_value) * 100
            weights.append(weight)
        
        if not weights:
            return 50
        
        max_weight = max(weights)
        
        if max_weight > 30:
            return 0
        elif max_weight > 25:
            return 40
        elif max_weight > 20:
            return 60
        elif max_weight > 15:
            return 80
        else:
            return 100
    
    @staticmethod
    def _sector_diversification_score(holdings, total_value):
        """Score based on sector allocation"""
        sector_weights = {}
        
        for h in holdings:
            sector_name = h.stock.sector.name if h.stock.sector else 'Unknown'
            weight = (float(h.current_value or 0) / total_value) * 100
            sector_weights[sector_name] = sector_weights.get(sector_name, 0) + weight
        
        if not sector_weights:
            return 0
        
        max_sector = max(sector_weights.values())
        num_sectors = len(sector_weights)
        
        score = 100
        
        if max_sector > 50:
            score -= 50
        elif max_sector > 40:
            score -= 30
        elif max_sector > 30:
            score -= 15
        
        if num_sectors >= 5:
            score += 0
        elif num_sectors >= 3:
            score -= 10
        elif num_sectors == 2:
            score -= 30
        else:
            score -= 50
        
        return max(0, min(100, score))
    
    @staticmethod
    def _holdings_count_score(count):
        """Score based on number of holdings"""
        if count >= 15:
            return 100
        elif count >= 10:
            return 90
        elif count >= 7:
            return 75
        elif count >= 5:
            return 60
        elif count >= 3:
            return 40
        else:
            return 20
    
    @staticmethod
    def get_sector_allocation(portfolio_id):
        """Get sector allocation as JSON"""
        holdings = Holding.objects.filter(portfolio_id=portfolio_id).select_related('stock', 'stock__sector')
        
        total_value = sum(float(h.current_value or 0) for h in holdings)
        
        if total_value == 0:
            return {}
        
        sector_allocation = {}
        for h in holdings:
            sector_name = h.stock.sector.name if h.stock.sector else 'Unknown'
            weight = (float(h.current_value or 0) / total_value) * 100
            sector_allocation[sector_name] = round(sector_allocation.get(sector_name, 0) + weight, 2)
        
        return sector_allocation
    
    @staticmethod
    def get_top_holdings(portfolio_id, limit=5):
        """Get top holdings as JSON"""
        holdings = Holding.objects.filter(portfolio_id=portfolio_id).select_related('stock').order_by('-current_value')[:limit]
        
        total_value = sum(float(h.current_value or 0) for h in Holding.objects.filter(portfolio_id=portfolio_id))
        
        if total_value == 0:
            return []
        
        top_holdings = []
        for h in holdings:
            weight = (float(h.current_value or 0) / total_value) * 100
            top_holdings.append({
                'symbol': h.stock.symbol,
                'name': h.stock.name,
                'weight': round(weight, 2),
                'value': float(h.current_value or 0)
            })
        
        return top_holdings
    
    @staticmethod
    def get_concentration_data(portfolio_id):
        """Get concentration metrics"""
        holdings = Holding.objects.filter(portfolio_id=portfolio_id).select_related('stock').order_by('-current_value')
        
        total_value = sum(float(h.current_value or 0) for h in holdings)
        
        if total_value == 0:
            return {}
        
        top_5_list = list(holdings[:5])
        top_5_value = sum(float(h.current_value or 0) for h in top_5_list)
        top_5_weight = (top_5_value / total_value) * 100
        
        first_holding = holdings.first()
        top_1_weight = (float(first_holding.current_value or 0) / total_value) * 100 if first_holding else 0
        
        return {
            'top_1_weight': round(top_1_weight, 2),
            'top_5_weight': round(top_5_weight, 2),
            'num_holdings': holdings.count()
        }
