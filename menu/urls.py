from django.urls import path
from . import views #  . = folderul curent


app_name = 'menu'

urlpatterns = [
    # ex: 8000/home/
    path('', views.HomeView), #nu mai adauga nimic la ruta

]