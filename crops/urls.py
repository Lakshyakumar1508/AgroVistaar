from django.urls import path
from . import views

app_name = "crops"

urlpatterns = [
    path('', views.crop_info_view, name='crop_info'),
]
