from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('api/<int:portfolio_id>/analysis/', views.get_portfolio_analysis, name='get_analysis'),
    path('api/<int:portfolio_id>/analyze/', views.run_portfolio_analysis, name='run_analysis'),
    path('api/<int:portfolio_id>/performance/', views.get_portfolio_performance, name='get_performance'),
    path('api/<int:portfolio_id>/recommendations/', views.get_recommendations, name='get_recommendations'),
]
