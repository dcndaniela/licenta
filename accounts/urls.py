from django.urls import path
from . import views #  . = folderul curent


app_name = 'accounts'

urlpatterns = [
    # ex: /accounts/login
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name = 'logout'),
    path('register/', views.RegisterView, name = 'register'),

]