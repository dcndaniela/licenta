from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import hashlib
from django.contrib.auth.hashers import BCryptSHA256PasswordHasher
from . import utils_functions
from datetime import datetime
import django.utils.timezone

class Election(models.Model):
    election_uuid = models.CharField(max_length = 50, null = False)
    election_title= models.CharField('Election name',max_length=200, default = 'Set an election name')
    election_content = models.CharField('Election content',max_length=200)
    pub_date = models.DateTimeField('date published',default= timezone.now, blank=True)
    start_date= models.DateTimeField(null= True) #setez default
    end_date= models.DateTimeField(null= True)
    isActive= models.BooleanField('PUBLISH',default = False) #devine True cand va fi facuta public
    def __str__(self): #aceasta functie exista pt fiecare obiect, deci ii fac override aici
        return self.election_title


class Voter(models.Model):
    #voter_id = models.CharField(max_length = 50, null = False) #id criptat al votantului
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    uuid = models.CharField(max_length = 50)
    voter_login_code = models.CharField(max_length = 100, null = True) #cod primit prin care se logheaza
    vote_hash = models.CharField(max_length = 100, null = True)
    cast_at = models.DateTimeField(auto_now_add = False, null = True)
    voter_email = models.CharField(max_length = 250, null = True)

    @property
    def get_user(self):
        return User.objects.filter(email=self.voter_email)

    @property
    def voter_id(self):
        return self.get_user().id

    @property
    def voter_id_hash(self):
            #return hashlib.sha256(self.voter_id)
            ha=BCryptSHA256PasswordHasher.encode(self, self.voter_id,BCryptSHA256PasswordHasher.salt())
            #return BCryptSHA256PasswordHasher.encode(self, self.voter_id,BCryptSHA256PasswordHasher.salt())
            print('voter_id_hash= {}'.format(ha))
            return ha


    def generate_voter_login_code(self, length = 10):
        if self.voter_login_code:
            raise Exception("password already exists")

        self.voter_login_code = utils_functions.random_string(length,
                                                        alphabet = 'abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')




class Choice(models.Model):#1 Choice apartine unei singure Election
    election = models.ForeignKey(Election, on_delete=models.CASCADE)#sterg Election => se sterg toate Choice pe care le are
    choice_text = models.CharField(max_length=200)
    #votes = models.IntegerField(default=0)
    choice_hash = models.CharField(max_length = 100, null = True, unique = True)
    # hash scurt pe care sa il pun in url
    choice_tinyhash = models.CharField(max_length = 50, null = True, unique = True)
    #voter = models.ForeignKey(Voter, on_delete = models.CASCADE)
    def __str__(self):
        return self.choice_text


# class Vote (models.Model):#1 Choice apartine unei singure Election
#     choice=   models.ForeignKey(Choice, on_delete=models.CASCADE)
#     #election = models.CharField(max_length = 200)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     vote_hash = models.CharField(max_length = 100,null = True, unique = True)
#     # hash scurt pe care sa il pun in url
#     vote_tinyhash = models.CharField(max_length = 50, null = True, unique = True)
#     #voter = models.ForeignKey(Voter, on_delete = models.CASCADE)

class AuditedBallot(models.Model):

  election = models.ForeignKey(Election, on_delete=models.CASCADE)
  raw_vote = models.TextField()
  vote_hash = models.CharField(max_length=100)
  added_at = models.DateTimeField(auto_now_add=True)

