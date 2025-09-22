# your_django_project/urls.py


from django.urls import path
from myapp import views 


app_name = 'myapp'

urlpatterns = [
    path('prediction/', views.prediction_view, name='prediction'),
    

]