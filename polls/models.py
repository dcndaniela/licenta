from django.db import models
from django.utils import timezone
from accounts.models import CustomUser as User
from django.core.validators import RegexValidator, MinLengthValidator



class Election(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE, null = True)
    election_title = models.CharField('Election name', max_length = 200, null = True,
                                      validators=[MinLengthValidator(5, message ="Election name should have at least 5 characters" ),
                                                  RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid election name.') ],unique = True )
    election_content = models.CharField('Election content', max_length = 200,
                                        validators=[MinLengthValidator(10, message ="Election content should have at least 10 characters" ),
                                                    RegexValidator(r'^[a-zA-Z0-9\s:?.]+$', 'Enter a valid election content.') ])
    created_at = models.DateTimeField(default = timezone.now, editable = False)#cand a fost creata
    modified_at = models.DateTimeField(auto_now_add=True,null=True)
    election_hash=models.CharField(max_length = 200, null = True)
    election_tinyhash = models.CharField(max_length = 50, null = True, unique = True)

    start_date = models.DateTimeField('Start date(yyyy-mm-dd hh:mm)',null = True)  # setez default
    end_date = models.DateTimeField('End date(yyyy-mm-dd hh:mm)',null = True)
    isActive = models.BooleanField('PUBLISH', default = False)  # devine True cand va fi facuta public

    result=models.CharField(max_length = 50, null = True)
    result_released_at = models.DateTimeField(null = True)

    p = models.IntegerField(default = 0) # ordin grup
    q = models.IntegerField(default = 0) # (p-1)/2
    g = models.IntegerField(default = 0) # nr random folosit la generare (pk,secret_key)
    public_key = models.IntegerField(default = 0) #cheia publica
    secret_key = models.IntegerField(default = 0) # cheia privata

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

    @property
    def has_ended(self):
        present = timezone.now()
        if(self.end_date <=present):
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
        max_votes=0
        for choice in self.choice_set.all():  # parinte acceseaza infos din copil
            d = {}
            d['text'] = choice.choice_text
            d['num_votes'] = choice.num_votes
            if choice.num_votes>max_votes:
                max_votes=choice.num_votes
            if not self.num_votes:
                d['percentage'] = 0
            else:
                perc = choice.num_votes / self.num_votes * 100
                d['percentage'] = float("{:.2f}".format(perc))
            res.append(d)
        #print (res)
        print(res)
        return res, max_votes

    @property
    def num_voters(self):
        return self.voter_set.count()


class Choice(models.Model):  # 1 Election are mai multe Choices
    election = models.ForeignKey(Election,on_delete = models.CASCADE)  # sterg Election => se sterg toate Choices pe care le are
    choice_text = models.CharField(max_length = 200,
                                   validators=[MinLengthValidator(5, message ="Choice text should have at least 5 characters" ),
                                               RegexValidator(r'^[a-zA-Z0-9\s]+$', 'Enter a valid choice text!') ])
    num_votes=models.IntegerField(default = 0)

    def __str__(self):
        return self.choice_text


class Voter(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    user = models.ForeignKey(User, null = True, on_delete = models.CASCADE)


class Vote(models.Model):  # ca un user sa NU poata vota de mai multe ori
    # models.PROTECT = daca sterg P(parinte), iar acesta are copii, nu il pot sterge (pe P)
    voter = models.OneToOneField(Voter, on_delete = models.CASCADE)  # sterg User=> sterg toate Votes asociate
    election = models.ForeignKey(Election, on_delete = models.CASCADE)  # sterg Election=> sterg toate Votes asociate
    cast_at = models.DateTimeField(auto_now_add = True, null= True)
    verified_at = models.DateTimeField(null = True)
    invalidated_at = models.DateTimeField(null = True)#este null daca este valid
    # alpha = models.IntegerField(default = 0)
    # beta = models.IntegerField(default = 0)


class AuditedBallot(models.Model):#retine doar voturile valide
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    text_vote = models.TextField(null = True)
    vote_hash = models.CharField(max_length = 200, null = True)
    added_at = models.DateTimeField(auto_now_add = True, null=True)


class Trustee(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    name = models.CharField(max_length = 200, null = True)
    public_key = models.IntegerField(default = 0)
    secret_key = models.IntegerField(default = 0)
    # False= sk a fost generata incorect; True=sk a fost generata corect
    posk = models.BooleanField(default = False)
