from django.db import models
import datetime
from django.utils import timezone

class Question(models.Model):
    question_title= models.CharField('Election name',max_length=200, default = 'Set an election name')
    question_content = models.CharField('Question',max_length=200)
    pub_date = models.DateTimeField('date published')
    start_date= models.DateTimeField(null= True) #setez default
    end_date= models.DateTimeField(null= True)
    isActive= models.BooleanField('PUBLISH',default = False) #devine True cand va fi facuta public
    def __str__(self): #aceasta functie exista pt fiecare obiect, deci ii fac override aici
        return self.question_title


class Choice(models.Model):#1 Choice apartine unei singure Question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)#sterg Question => se sterg toate Choice pe care le are
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text