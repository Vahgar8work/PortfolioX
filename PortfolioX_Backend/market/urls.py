from django.urls import path
from . import views

urlpatterns = []
urlpatterns += [
    path('api/populate-stock/', views.add_and_populate_stock),
]
