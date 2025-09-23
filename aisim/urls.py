"""
URL configuration for the 'aisim' application.
"""
from django.urls import path
from . import views  # Assuming your views.py is in the same 'aisim' app directory

app_name = 'aisim'
urlpatterns = [
    # This maps the root of the included URL ('/ai_simulator/')
    # to the ai_simulator_view.
    path('', views.ai_simulator_view, name='ai_simulator'),
]
