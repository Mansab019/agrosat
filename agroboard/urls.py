from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.index, name = 'index'),
    path('api/indices/', views.api_indices, name = 'api_indices'),
    path('api/timeseries/', views.api_timeseries, name = 'api_timeseries'),
    path('api/classify/', views.api_classify, name='api_classify'),
]

