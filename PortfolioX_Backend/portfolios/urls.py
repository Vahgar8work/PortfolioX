from django.urls import path
from . import views

urlpatterns = [
    path('api/create-portfolio/', views.create_portfolio),
    path('api/add-holding/', views.add_holding),
    path('api/add-transaction/', views.add_transaction),
]
