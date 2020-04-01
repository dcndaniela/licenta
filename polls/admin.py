from django.contrib import admin
from .models import Question,Choice

# Register your models here.

admin.site.register(Question)  #ca sa fie vizibile pt Admin
admin.site.register(Choice)#ca sa fie vizibile pt Admin