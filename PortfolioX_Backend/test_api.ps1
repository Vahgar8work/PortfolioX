# setup_test_data.ps1
# Create test portfolio and data for analytics

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting Up Test Data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$py = if (Test-Path "venv/Scripts/python.exe") { "venv/Scripts/python.exe" } else { "python" }

# Create Python script to set up test data
$setupScript = @'
import os
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from portfolios.models import Portfolio, Holding
from market.models import Stock, Sector, Benchmark, BenchmarkPriceHistory, StockPriceHistory
from analytics.models import PortfolioValueHistory

User = get_user_model()

print("=" * 50)
print("Creating Test Data")
print("=" * 50)

# 1. Create user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"\nCreated user: {user.username}")
else:
    print(f"\nUsing existing user: {user.username}")

# 2. Create sectors
sectors_data = ['Technology', 'Finance', 'Healthcare', 'Consumer', 'Energy']
sectors = {}
for sector_name in sectors_data:
    sector, created = Sector.objects.get_or_create(
        name=sector_name,
        defaults={'description': f'{sector_name} sector'}
    )
    sectors[sector_name] = sector
print(f"Created {len(sectors)} sectors")

# 3. Create benchmark
benchmark, created = Benchmark.objects.get_or_create(
    symbol='NIFTY50',
    defaults={
        'name': 'NIFTY 50',
        'description': 'NSE NIFTY 50 Index',
        'current_value': Decimal('21500.00')
    }
)
print(f"Benchmark: {benchmark.symbol}")

# 4. Create benchmark price history
if BenchmarkPriceHistory.objects.filter(benchmark=benchmark).count() == 0:
    print("  Creating benchmark price history...")
    base_price = 20000
    for i in range(365, 0, -1):
        date = datetime.now().date() - timedelta(days=i)
        price = base_price + random.randint(-500, 500)
        BenchmarkPriceHistory.objects.create(
            benchmark=benchmark,
            trade_date=date,
            open_value=price,
            high_value=price + 100,
            low_value=price - 100,
            close_value=price
        )
    print(f"  Created 365 days of benchmark history")
else:
    print("  Benchmark history exists")

# 5. Create stocks
stocks_data = [
    ('RELIANCE', 'Reliance Industries', 'Technology', 2450.50),
    ('TCS', 'Tata Consultancy Services', 'Technology', 3650.75),
    ('INFY', 'Infosys', 'Technology', 1580.25),
    ('HDFCBANK', 'HDFC Bank', 'Finance', 1650.80),
    ('ICICIBANK', 'ICICI Bank', 'Finance', 980.40),
    ('SBIN', 'State Bank of India', 'Finance', 610.30),
    ('ITC', 'ITC Limited', 'Consumer', 425.60),
    ('HINDUNILVR', 'Hindustan Unilever', 'Consumer', 2380.90),
]

stocks = {}
for symbol, name, sector_name, price in stocks_data:
    stock, created = Stock.objects.get_or_create(
        symbol=symbol,
        defaults={
            'name': name,
            'sector': sectors[sector_name],
            'current_price': Decimal(str(price)),
            'exchange': 'NSE',
            'isin': f'INE{symbol[:6]}'
        }
    )
    stocks[symbol] = stock
    
    if StockPriceHistory.objects.filter(stock=stock).count() == 0:
        base_price = float(price)
        for i in range(365, 0, -1):
            date = datetime.now().date() - timedelta(days=i)
            daily_price = base_price * (1 + random.uniform(-0.03, 0.03))
            StockPriceHistory.objects.create(
                stock=stock,
                trade_date=date,
                open_price=daily_price,
                high_price=daily_price * 1.02,
                low_price=daily_price * 0.98,
                close_price=daily_price,
                volume=random.randint(100000, 1000000)
            )

print(f"Created {len(stocks)} stocks with price history")

# 6. Create portfolio
portfolio, created = Portfolio.objects.get_or_create(
    user=user,
    name='Test Portfolio',
    defaults={
        'description': 'Sample portfolio for testing analytics',
        'benchmark': benchmark,
        'is_active': True
    }
)
if created:
    print(f"\nCreated portfolio: {portfolio.name} (ID: {portfolio.id})")
else:
    print(f"\nUsing existing portfolio: {portfolio.name} (ID: {portfolio.id})")

# 7. Create holdings
holdings_data = [
    ('RELIANCE', 50, 2400.00),
    ('TCS', 30, 3500.00),
    ('INFY', 100, 1550.00),
    ('HDFCBANK', 40, 1600.00),
    ('ICICIBANK', 80, 950.00),
    ('SBIN', 150, 600.00),
    ('ITC', 200, 420.00),
    ('HINDUNILVR', 25, 2350.00),
]

if Holding.objects.filter(portfolio=portfolio).count() == 0:
    for symbol, quantity, avg_price in holdings_data:
        stock = stocks[symbol]
        current_value = float(stock.current_price) * quantity
        invested_value = avg_price * quantity
        
        Holding.objects.create(
            portfolio=portfolio,
            stock=stock,
            quantity=quantity,
            avg_buy_price=Decimal(str(avg_price)),
            current_value=Decimal(str(current_value)),
            invested_value=Decimal(str(invested_value)),
            gain_loss=Decimal(str(current_value - invested_value)),
            buy_date=datetime.now().date() - timedelta(days=random.randint(30, 365))
        )
    print(f"Created {len(holdings_data)} holdings")
else:
    print("Holdings already exist")

# 8. Update portfolio totals
holdings = Holding.objects.filter(portfolio=portfolio)
total_invested = sum(float(h.invested_value or 0) for h in holdings)
total_current = sum(float(h.current_value or 0) for h in holdings)

portfolio.total_invested = Decimal(str(total_invested))
portfolio.current_value = Decimal(str(total_current))
portfolio.total_gain_loss = Decimal(str(total_current - total_invested))
if total_invested > 0:
    portfolio.total_gain_pct = (portfolio.total_gain_loss / portfolio.total_invested) * 100
portfolio.save()

print(f"Portfolio value: Rs {total_current:,.2f}")

# 9. Create portfolio value history
if PortfolioValueHistory.objects.filter(portfolio=portfolio).count() == 0:
    print("  Creating portfolio value history...")
    for i in range(90, 0, -1):
        date = datetime.now().date() - timedelta(days=i)
        value = total_current * (1 + random.uniform(-0.02, 0.02))
        PortfolioValueHistory.objects.create(
            portfolio=portfolio,
            record_date=date,
            total_value=Decimal(str(value)),
            invested_value=Decimal(str(total_invested))
        )
    print(f"  Created 90 days of portfolio history")
else:
    print("  Portfolio history exists")

print("\n" + "=" * 50)
print("TEST DATA READY")
print("=" * 50)
print(f"\nPortfolio ID: {portfolio.id}")
print(f"Portfolio Name: {portfolio.name}")
print(f"Holdings: {holdings.count()}")
print(f"Total Value: Rs {total_current:,.2f}")
print(f"\nTest portfolio created! Use portfolio ID: {portfolio.id}")
print("=" * 50)
'@

Set-Content -Path "setup_test_data.py" -Value $setupScript

Write-Host "Creating test data (this may take a minute)..." -ForegroundColor Yellow
Write-Host ""

try {
    & $py setup_test_data.py
    Write-Host ""
    Write-Host "Test data created successfully!" -ForegroundColor Green
    Write-Host ""
    $success = $true
}
catch {
    Write-Host ""
    Write-Host "Error creating test data: $_" -ForegroundColor Red
    Write-Host ""
    $success = $false
}

Remove-Item "setup_test_data.py" -ErrorAction SilentlyContinue

if ($success) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Testing Analytics API" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Start-Sleep -Seconds 2
    
    $portfolioId = 2
    $baseUrl = "http://localhost:8000/analytics/api"
    
    Write-Host "[1/3] Running analysis..." -ForegroundColor Yellow
    try {
        $result = Invoke-RestMethod "${baseUrl}/${portfolioId}/analyze/" -Method POST
        Write-Host "  SUCCESS: $($result.message)" -ForegroundColor Green
        Write-Host "  Health Score: $($result.health_score)/100" -ForegroundColor Green
        Write-Host ""
    }
    catch {
        Write-Host "  FAILED: $_" -ForegroundColor Red
        Write-Host ""
    }
    
    Start-Sleep -Seconds 2
    
    Write-Host "[2/3] Getting analysis results..." -ForegroundColor Yellow
    try {
        $analysis = Invoke-RestMethod "${baseUrl}/${portfolioId}/analysis/" -Method GET
        Write-Host "  Portfolio: $($analysis.portfolio_name)" -ForegroundColor Green
        Write-Host "  Health Score: $($analysis.health_score)/100" -ForegroundColor White
        Write-Host "  Diversification: $($analysis.diversification_score)/100" -ForegroundColor White
        Write-Host "  YTD Return: $($analysis.returns.ytd)%" -ForegroundColor White
        Write-Host "  Alpha: $($analysis.benchmark_comparison.alpha)" -ForegroundColor White
        Write-Host "  Beta: $($analysis.benchmark_comparison.beta)" -ForegroundColor White
        Write-Host ""
    }
    catch {
        Write-Host "  FAILED: $_" -ForegroundColor Red
        Write-Host ""
    }
    
    Write-Host "[3/3] Getting recommendations..." -ForegroundColor Yellow
    try {
        $recs = Invoke-RestMethod "${baseUrl}/${portfolioId}/recommendations/" -Method GET
        Write-Host "  Total: $($recs.recommendations.Count) recommendations" -ForegroundColor Green
        foreach ($rec in $recs.recommendations) {
            Write-Host "    [$($rec.priority)] $($rec.message)" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    catch {
        Write-Host "  FAILED: $_" -ForegroundColor Red
        Write-Host ""
    }
    
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Testing Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
}
