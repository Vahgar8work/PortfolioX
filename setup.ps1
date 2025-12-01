$ErrorActionPreference = "Stop"
$ProjectName = "PortfolioX_Backend"
$VenvName = "venv"

Write-Host "Setting up Django project..."

# Step 1: Make project folder and enter it
if (!(Test-Path $ProjectName)) {
    New-Item -ItemType Directory $ProjectName | Out-Null
}
Set-Location $ProjectName

# Step 2: Create virtual environment
if (!(Test-Path $VenvName)) {
    python -m venv $VenvName
}
$Py = Join-Path $VenvName "Scripts\python.exe"
$Pip = Join-Path $VenvName "Scripts\pip.exe"

if (!(Test-Path $Py)) {
    Write-Error "Python executable not found after venv."
    exit 1
}

# Step 3: Install dependencies
& $Pip install --upgrade pip | Out-Null
& $Pip install django djangorestframework django-cors-headers psycopg2-binary celery redis pandas numpy python-dotenv | Out-Null

# Step 4: Start Django project
if (!(Test-Path "manage.py")) {
    & $Py -m django startproject config .
}

# Step 5: Start Django apps
$Apps = @("users", "market", "portfolios", "analytics", "core")
foreach ($App in $Apps) {
    if (!(Test-Path $App)) {
        & $Py manage.py startapp $App
    }
}

# Step 6: Create .env
$SecretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | ForEach-Object {[char]$_})
$EnvContent = @"
DEBUG=True
SECRET_KEY=django-insecure-$SecretKey
DB_NAME=portfoliox_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
"@
Set-Content .env -Encoding UTF8 -Value $EnvContent

# Step 7: Write models

$UsersModels = @"
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('retail', 'Retail'),
        ('premium', 'Premium'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='retail')
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['role'], name='idx_users_role'),
        ]
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_sessions_user'),
            models.Index(fields=['token_hash'], name='idx_sessions_token'),
        ]
"@
Set-Content users/models.py -Encoding UTF8 -Value $UsersModels

$MarketModels = @"
from django.db import models

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    EXCHANGE_CHOICES = [('NSE', 'NSE'), ('BSE', 'BSE')]
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    exchange = models.CharField(max_length=10, choices=EXCHANGE_CHOICES, default='NSE')
    isin = models.CharField(max_length=12, null=True, blank=True)
    current_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    previous_close = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    day_change = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    day_change_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['symbol'], name='idx_stocks_symbol'),
            models.Index(fields=['sector'], name='idx_stocks_sector'),
        ]
class StockPriceHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    trade_date = models.DateField()
    open_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    high_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    low_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField(null=True)
    daily_return = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['stock', 'trade_date']
        indexes = [
            models.Index(fields=['stock', '-trade_date'], name='idx_price_history_stock_date'),
            models.Index(fields=['trade_date'], name='idx_price_history_date'),
        ]
class BenchmarkIndex(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    last_updated = models.DateTimeField(null=True)
class BenchmarkPriceHistory(models.Model):
    benchmark = models.ForeignKey(BenchmarkIndex, on_delete=models.CASCADE)
    trade_date = models.DateField()
    close_value = models.DecimalField(max_digits=12, decimal_places=2)
    daily_return = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    class Meta:
        unique_together = ['benchmark', 'trade_date']
"@
Set-Content market/models.py -Encoding UTF8 -Value $MarketModels

$PortfoliosModels = @"
from django.db import models
from django.conf import settings
from market.models import Stock, BenchmarkIndex

class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    benchmark = models.ForeignKey(BenchmarkIndex, on_delete=models.SET_NULL, null=True, default=1)
    total_invested = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_gain_loss = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_gain_pct = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    day_change = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    day_change_pct = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['user', 'name']

class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, related_name='holdings', on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    avg_buy_price = models.DecimalField(max_digits=12, decimal_places=2)
    buy_date = models.DateField(null=True)
    invested_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    current_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    gain_loss = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    weight_pct = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['portfolio', 'stock']

class PortfolioTransaction(models.Model):
    TYPE_CHOICES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
"@
Set-Content portfolios/models.py -Encoding UTF8 -Value $PortfoliosModels

$AnalyticsModels = @"
from django.db import models
from portfolios.models import Portfolio

class AnalysisResult(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    analysis_date = models.DateField()
    health_score = models.IntegerField()
    diversification_score = models.IntegerField()
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    sharpe_ratio = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    return_1d = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    return_ytd = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    alpha = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    beta = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    sector_allocation = models.JSONField(default=dict)
    top_holdings = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['portfolio', 'analysis_date']
        indexes = [
            models.Index(fields=['portfolio', '-analysis_date'], name='idx_analysis_pf_date'),
        ]

class PortfolioValueHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    record_date = models.DateField()
    total_value = models.DecimalField(max_digits=14, decimal_places=2)
    invested_value = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    class Meta:
        unique_together = ['portfolio', 'record_date']
"@
Set-Content analytics/models.py -Encoding UTF8 -Value $AnalyticsModels

$CoreModels = @"
from django.db import models
from django.conf import settings
from portfolios.models import Portfolio

class Alert(models.Model):
    PRIORITY_CHOICES = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    TYPE_CHOICES = [
        ('concentration_risk', 'Concentration Risk'),
        ('sector_imbalance', 'Sector Imbalance'),
        ('price_alert', 'Price Alert'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True)
    alert_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=['user'], name='idx_alerts_user_unread', condition=models.Q(is_read=False)),
        ]
class UploadJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('processing', 'Processing'),
        ('completed', 'Completed'), ('failed', 'Failed')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_log = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
"@
Set-Content core/models.py -Encoding UTF8 -Value $CoreModels

# Step 8: Update config/settings.py for .env and Postgres
$SettingsPath = "config/settings.py"
$SettingsContent = Get-Content $SettingsPath -Raw -Encoding UTF8

$dotenvImport = @"
import os
from dotenv import load_dotenv
load_dotenv()
"@

$SettingsContent = $dotenvImport + $SettingsContent
$SettingsContent = $SettingsContent -replace "DATABASES = \{[\s\S]+?\}", @"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'portfoliox_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
"@

$CORS_USER_CONFIG = @"
CORS_ALLOW_ALL_ORIGINS = True
AUTH_USER_MODEL = 'users.User'
"@
$SettingsContent = $SettingsContent + $CORS_USER_CONFIG

Set-Content -Path $SettingsPath -Encoding UTF8 -Value $SettingsContent

# Step 9: Run migrations
& $Py manage.py makemigrations users market portfolios analytics core
& $Py manage.py migrate

Write-Host "Setup complete. You can now run: python manage.py runserver"
