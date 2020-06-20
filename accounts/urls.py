from django.urls import path
from . import views #  . = folderul curent


app_name = 'accounts'

urlpatterns = [

    path('failed_login/', views.FailedLogInView, name='failed_login'),
    path('login/', views.LoginView, name='login'),# ex: /accounts/login
    path('logout/', views.LogoutView, name = 'logout'),
    path('register/', views.RegisterView, name = 'register'),
    path('change_password/', views.ChangePasswordView, name='change_password'),

]