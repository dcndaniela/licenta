from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
# from django.contrib.auth.models import(
#         AbstractBaseUser
#     )
#
# class User(AbstractBaseUser):  #clasa User pe care o scriu eu, ca sa inlocuiasca User django class
#     email=
# from django.contrib.auth.models import AbstractUser
#
#
# class CustomUser(AbstractUser):
#     cnp= models.CharField('CNP',min_length=13,max_length = 13, null = False)
#     #phone= models.CharField('Phone',min_length=10,max_length = 10, null = False)
#     phone=models.CharField('Phone',min_length=10,max_length = 10, null = False,
#                     error_messages={'incomplete': 'Enter a phone number.'},
#                     validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')])
#     password=models.CharField('Password',min_length=11, null = False)
