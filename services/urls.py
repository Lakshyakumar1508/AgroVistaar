from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),           # Home page
    path('profile/', views.profile, name='profile'),     
    path('services/', views.services, name='services'),     
    path('soilInfo/', views.soilInfo, name='soilInfo'),     
    path('about/', views.about, name='about'),     
    path('chatbot/', include('chatbot.urls')),       
    path('', include('loginsignup.urls')),          
    path('', include('myapp.urls')),  
]
