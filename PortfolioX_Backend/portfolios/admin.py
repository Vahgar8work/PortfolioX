from django.contrib import admin
from .models import Portfolio, Holding, PortfolioTransaction

admin.site.register(Portfolio)
admin.site.register(Holding)
admin.site.register(PortfolioTransaction)