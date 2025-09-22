from django.urls import path
from . import views

app_name = 'chatbot'  
urlpatterns = [
    path('', views.chat_view, name='chat_page'),
    path('api/', views.chat_view, name='chat_api') 
]



