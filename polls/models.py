import bleach
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser as User
from django.contrib.auth.hashers import BCryptSHA256PasswordHasher
from .crypto import utils_functions
from polls import algoritmi
from django.core.validators import MinLengthValidator
import datetime
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
#
# class PublicKey(models.model):


class Election(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE, default = 1)
    election_uuid = models.CharField(max_length = 200, null = True, default=True)
    # election_uuid= models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    election_title = models.CharField('Election name', max_length = 200, null = True,
                                      validators=[MinLengthValidator(5, message ="Election name should have at least 5 characters" ),
                                                  RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid election name.') ] )
    election_content = models.CharField('Election content', max_length = 200,
                                        validators=[MinLengthValidator(10, message ="Election content should have at least 10 characters" ),
                                                    RegexValidator(r'^[a-zA-Z0-9\s:?.]+$', 'Enter a valid election content.') ])
    pub_date = models.DateTimeField('date published', default = timezone.now, blank = True)#cand a fost creata
    modified_at = models.DateTimeField(auto_now_add=True,null=True)
    election_hash=models.CharField(max_length = 200, null = True)
    election_tinyhash = models.CharField(max_length = 50, null = True, unique = True)

    # encrypted_tally=models.CharField(max_length = 250, null = True)

    start_date = models.DateTimeField('Start date(yyyy-mm-dd hh:mm)',null = True)  # setez default
    end_date = models.DateTimeField('End date(yyyy-mm-dd hh:mm)',null = True)
    isActive = models.BooleanField('PUBLISH', default = False)  # devine True cand va fi facuta public

    result=models.CharField(max_length = 50, null = True)
    result_released_at = models.DateTimeField(auto_now_add = False, default = None, null = True)

    public_key = models.IntegerField(default = 0) #cheia publica
    secret_key = models.IntegerField(default = 0) # cheia privata
    p = models.IntegerField(default = 0) # ordin grup
    q = models.IntegerField(default = 0) # (p-1)/2
    g = models.IntegerField(default = 0) # nr random folosit la gnerare (pk,secret_key)


    #num_votes= models.PositiveIntegerField(default = 0)

    # tallying_starts_at = models.DateTimeField(auto_now_add = False, default = None, null = True)
    # encrypted_tally=models.CharField(max_length = 200, null = True)
    # result=models.CharField(max_length = 50, null = True)

    def __str__(self):  # aceasta functie exista pt fiecare obiect, deci ii fac override aici
        return self.election_title

    @property
    def can_see_results(self):  # rezultatele se afiseaza dupa ce s-a incheiat perioada de vot
        if self.end_date <= timezone.now():
            return True
        return False

    @property
    def has_not_started(self):
        present=timezone.now()
        #True daca Election NU a inceput inca
        if (self.start_date<=present and present<=self.end_date):
            return False
        return True

    #@property
    def is_first_vote_for_this_election(self, user):
        # returneaza True daca userul NU a votat inca
        voter=Voter.objects.filter(user=user).filter(election=self)
        print(voter)
        if voter.exists():
            return False
        return True

    @property  # ca sa pot apela num_votes-proprietate, in loc de num_votes() -functie
    #astfel o pot apela in templates (html)
    def num_votes(self):
        return self.vote_set.count()

    def get_results_dict(self):
        # returneaza o lista de obiecte de forma
        # [
        #     pt fiecare choice din aceasta Election
        #     {
        #         'text':choice_text,
        #         'num_votes': nr de voturi primite de choice curenta
        #         'percentage': num_votes/ election.num_votes *100 (voturi primite/voturi totale *100)
        #         }
        #     ]
        res = []
        # self= Election ( aka pointerul this)
        for choice in self.choice_set.all():  # parinte acceseaza infos din copil
            d = {}
            d['text'] = choice.choice_text
            d['num_votes'] = choice.num_votes
            if not self.num_votes:
                d['percentage'] = 0
            else:
                perc = choice.num_votes / self.num_votes * 100
                d['percentage'] = float("{:.2f}".format(perc))
            res.append(d)
        #print (res)
        return res

    @property
    def num_voters(self):
        return self.voter_set.count()

    @property
    def description_bleached(self):
        return bleach.clean(self.description, tags = bleach.ALLOWED_TAGS + ['p', 'h4', 'h5', 'h3', 'h2', 'br', 'u'])

    # def generate_Trustee1(self):
    #     # creez Trustee1 care foloseste pk,sk pentru Election
    #     trustee = Trustee(election = self)
    #     trustee.name = "Trustee1"
    #     trustee.public_key = self.public_key
    #     trustee.secret_key = self.secret_key
    #     trustee.posk = algoritmi.ZKProofIACR_Trustee_verify_sk(self.p,self.g,self.q,self.secret_key,self.public_key)
    #     trustee.save()

    # def generate_Trustee2(self):
    #     public_key,secret_key = algoritmi.generateEG_pk_sk(self.p, self.q, self.g)
    #     # creez Trustee
    #     trustee = Trustee(election = self)
    #     trustee.name = "Trustee2"
    #     trustee.public_key = public_key
    #     trustee.secret_key = secret_key
    #     trustee.posk = algoritmi.ZKProofIACR_Trustee_verify_sk(self.p,self.g,self.q,secret_key,public_key)
    #     trustee.save()


class Choice(models.Model):  # 1 Election are mai multe Choices
    election = models.ForeignKey(Election,on_delete = models.CASCADE)  # sterg Election => se sterg toate Choices pe care le are
    choice_text = models.CharField(max_length = 200,
                                   validators=[MinLengthValidator(5, message ="Choice text should have at least 5 characters" ),
                                               RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid choice text!') ])
    # votes = models.IntegerField(default=0)
    #choice_hash = models.CharField(max_length = 100, null = True, unique = True)
    # hash scurt pe care sa il pun in url
    #choice_tinyhash = models.CharField(max_length = 50, null = True, unique = True)

    # voter = models.ForeignKey(Voter, on_delete = models.CASCADE)
    # nr_votes=models.IntegerField(default = 0)
    def __str__(self):
        return self.choice_text

    @property
    def num_votes(self):
        return self.vote_set.count()  # nr de voturi primite de aceasta choice

class Voter(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    user = models.ForeignKey(User, null = True, on_delete = models.CASCADE)
    #vote_hash = models.CharField(max_length = 250, null=True)
    #uuid=models.CharField(max_length = 200, null = True)
    #voter_login_code = models.CharField(max_length = 100, null = True) #cod primit prin care se logheaza


#     def generate_voter_login_code(self, length = 10):
#         if self.voter_login_code:
#             raise Exception("password already exists")
#
#         self.voter_login_code = utils_functions.random_string(length,
#                                         alphabet = 'abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')


class Vote(models.Model):  # ca un user sa NU poata vota de mai multe ori
    # models.PROTECT = daca sterg P(parinte), iar acesta are copii, nu il pot sterge (pe P)
    voter = models.OneToOneField(Voter, on_delete = models.CASCADE)  # sterg User=> sterg toate Votes asociate
    election = models.ForeignKey(Election, on_delete = models.CASCADE)  # sterg Election=> sterg toate Votes asociate
    choice = models.ForeignKey(Choice, on_delete = models.CASCADE)  # sterg Choice=> sterg toate Votes asociate

    #vote_hash = models.CharField(max_length = 200, null = True)
    cast_at = models.DateTimeField(auto_now_add = True, null = True)

    verified_at = models.DateTimeField(null = True)
    invalidated_at = models.DateTimeField(null = True)#este null daca este valid

    # alpha = models.IntegerField(default = 0)
    # beta = models.IntegerField(default = 0)

    # c1 = models.IntegerField(default=0)
    # c2 = models.IntegerField(default = 0)


class AuditedBallot(models.Model):#retine doar voturile valide
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    text_vote = models.TextField(null = True)
    vote_hash = models.CharField(max_length = 200, null = True)
    added_at = models.DateTimeField(auto_now_add = True, null = True)


class Trustee(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)

    name = models.CharField(max_length = 200, null = True)
    #secret = models.CharField(max_length = 100, null = True)

    # public key
    public_key = models.IntegerField(default = 0)
    public_key_hash = models.CharField(max_length = 100, null = True)

    # if the secret key is present, this means Helios is playing the role of the trustee.
    secret_key = models.IntegerField(default = 0)

    # False= sk a fost generata incorect; True=sk a fost generata corect
    posk = models.BooleanField(default = False)#
