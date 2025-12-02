# test_analytics.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from portfolios.models import Portfolio
from analytics.services.analyzer import PortfolioAnalyzer

print("=" * 50)
print("PortfolioX Analytics Engine Test")
print("=" * 50)

portfolios = Portfolio.objects.all()

if not portfolios.exists():
    print("\nNo portfolios found!")
    print("Create a portfolio first using the API.")
    exit()

portfolio = portfolios.first()
print(f"\nTesting portfolio: {portfolio.name} (ID: {portfolio.id})")
print("-" * 50)

try:
    result = PortfolioAnalyzer.analyze_portfolio(portfolio.id)
    
    if result:
        print("\nANALYSIS RESULTS:")
        print("-" * 50)
        print(f"Health Score:         {result.get('health_score')}/100")
        print(f"Diversification:      {result.get('diversification_score')}/100")
        print(f"YTD Return:           {result.get('return_ytd')}%")
        print(f"Alpha:                {result.get('alpha')}")
        print(f"Beta:                 {result.get('beta')}")
        print(f"Sharpe Ratio:         {result.get('sharpe_ratio')}")
        print(f"Volatility (30d):     {result.get('volatility_30d')}")
        print(f"Recommendations:      {len(result.get('recommendations', []))}")
        
        print("\nRECOMMENDATIONS:")
        print("-" * 50)
        for i, rec in enumerate(result.get('recommendations', []), 1):
            print(f"{i}. [{rec.get('priority').upper()}] {rec.get('message')}")
        
        print("\n" + "=" * 50)
        print("SUCCESS: Analysis completed!")
        print("=" * 50)
    else:
        print("\nERROR: Analysis returned no results")
        print("Ensure portfolio has holdings with price history.")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
