import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinLengthValidator, MaxLengthValidator


class MyAccountManager(BaseUserManager):
    def create_user(self,cnp,phone,password):
        if not cnp:
            raise ValueError("CNP is required")
        if not phone:
            raise ValueError("Phone number is required")
      #  if not password:
      #      raise ValueError("Password is required")

        user=self.model(
            cnp=cnp,
            phone=phone,
            #password=password,
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cnp, phone, password):
        user = self.create_user(
            cnp = cnp,
            phone = phone,
            password=password,
            )
        user.is_admin= True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    cnp= models.CharField(verbose_name = 'CNP',max_length = 13, null = False,unique=True,
                          validators=[MinLengthValidator(13, message ="CNP should have 13 digits!"),
                                      MaxLengthValidator(13, message = "CNP should have 13 digits!"),
                                      RegexValidator(r'^[1-9]+[0-9]+$', 'Enter a valid CNP, formed with digits only!')])

    phone=models.CharField(verbose_name = 'Phone', max_length = 10, null = False,unique=True,
                           validators = [MinLengthValidator(10, message ="Phone number should have 10 digits!"),
                                         MaxLengthValidator(10, message = "Phone number should have 10 digits!"),
                                         RegexValidator(r'^07[0-9]+$','Enter a valid Phone number, formed with digits only!')]
                           )
    alias = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)

    #acestea sunt fields required:
    username= models.CharField(max_length = 30,null=True, default = 'user')
    date_joined=models.DateTimeField(verbose_name = 'date joined',auto_now_add = True)
    last_login = models.DateTimeField(verbose_name = 'last login',auto_now_add = True)
    is_admin= models.BooleanField(default = False)
    is_active = models.BooleanField(default = True)
    is_staff = models.BooleanField(default = False)
    is_superuser = models.BooleanField(default = False)

    USERNAME_FIELD='cnp'
    REQUIRED_FIELDS=['phone','password',]

    objects=MyAccountManager()

    def __str__(self):
        return self.phone

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,app_label):
        return True

















