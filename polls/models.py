import bleach
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser as User
from django.contrib.auth.hashers import BCryptSHA256PasswordHasher
from .crypto import utils_functions
import datetime
import uuid
from django.core.exceptions import ObjectDoesNotExist

#
# class PublicKey(models.model):


class Election(models.Model):
    owner = models.ForeignKey(User, on_delete = models.CASCADE, default = 1)
    election_uuid = models.CharField(max_length = 200, null = True, default=True)
    # election_uuid= models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    election_title = models.CharField('Election name', max_length = 200, default = 'Set an election name')
    election_content = models.CharField('Election content', max_length = 200)
    pub_date = models.DateTimeField('date published', default = timezone.now, blank = True)#cand a fost creata
    modified_at = models.DateTimeField(auto_now_add=True,null=True)
    election_hash=models.CharField(max_length = 200, null = True)
    election_tinyhash = models.CharField(max_length = 50, null = True, unique = True)

    # encrypted_tally=models.CharField(max_length = 250, null = True)

    start_date = models.DateTimeField(null = True)  # setez default
    end_date = models.DateTimeField(null = True)
    isActive = models.BooleanField('PUBLISH', default = False)  # devine True cand va fi facuta public

    result=models.CharField(max_length = 50, null = True)
    result_released_at = models.DateTimeField(auto_now_add = False, default = None, null = True)

    public_key = models.IntegerField(default = 0) # prin ElGamal
    private_key = models.IntegerField(default = 0)

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
        #poate fi modificata daca Election nu a inceput
        if (self.start_date<=present and present<=self.end_date):
            return False
        return True

    #@property
    def user_can_vote(self, user):
        # returneaza True daca userul NU a votat inca
        voter=Voter.objects.filter(user=user).filter(election=self)
        #voter2=voter.filter(election=self)
        print(voter)
        #user_votes = Vote.objects.filter(voter=voter)
        #qs = user_votes.filter(election = self)
        #print ('aici este ')
        #print(qs)
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


    # @property
    # def encrypted_tally_hash(self):
    #     if not self.encrypted_tally:
    #         return None
    #
    #     return utils_functions.hash_b64(self.encrypted_tally)

    @property
    def description_bleached(self):
        return bleach.clean(self.description, tags = bleach.ALLOWED_TAGS + ['p', 'h4', 'h5', 'h3', 'h2', 'br', 'u'])

    # @property
    # def issues_before_freeze(self):
    #     issues = []
    #     if self.questions == None or len(self.questions) == 0:
    #         issues.append(
    #             {
    #                 'type': 'questions',
    #                 'action': "add questions to the ballot"
    #                 }
    #             )
    #
    #     trustees = Trustee.get_by_election(self)
    #     if len(trustees) == 0:
    #         issues.append({
    #             'type': 'trustees',
    #             'action': "add at least one trustee"
    #             })
    #
    #     for t in trustees:
    #         if t.public_key == None:
    #             issues.append({
    #                 'type': 'trustee keypairs',
    #                 'action': 'have trustee %s generate a keypair' % t.name
    #                 })
    #
    #     if self.voter_set.count() == 0 and not self.openreg:
    #         issues.append({
    #             "type": "voters",
    #             "action": 'enter your voter list (or open registration to the public)'
    #             })
    #
    #     return issues

    # def ready_for_tallying(self):
    #     return datetime.datetime.now() >= self.tallying_starts_at

    # def compute_tally(self):
    #     """
    #     tally the election, assuming votes already verified
    #     """
    #     tally = self.init_tally()
    #     for voter in self.voter_set.exclude(vote = None):
    #         tally.add_vote(voter.vote, verify_p = False)
    #
    #     self.encrypted_tally = tally
    #     self.save()

    # def init_tally(self):
    #     # FIXME: create the right kind of tally
    #     from helios.workflows import homomorphic
    #     return homomorphic.Tally(election = self)
    #
    # def ready_for_decryption(self):
    #     return self.encrypted_tally != None

    # def ready_for_decryption_combination(self):
    #     """
    #     do we have a tally from all trustees?
    #     """
    #     for t in Trustee.get_by_election(self):
    #         if not t.decryption_factors:
    #             return False
    #
    #     return True

    def release_result(self):
        """
        release the result that should already be computed
        """
        if not self.result:
            return

        self.result_released_at = datetime.datetime.utcnow()

    # def combine_decryptions(self):
    #     """
    #     combine all of the decryption results
    #     """
    #
    #     # gather the decryption factors
    #     trustees = Trustee.get_by_election(self)
    #     decryption_factors = [t.decryption_factors for t in trustees]
    #
    #     self.result = self.encrypted_tally.decrypt_from_factors(decryption_factors, self.public_key)
    #
    #     #self.append_log(ElectionLog.DECRYPTIONS_COMBINED)
    #
    #     self.save()

    # def generate_trustee(self, params):
    #     """
    #     generate a trustee including the secret key,
    #     thus a helios-based trustee
    #     """
    #     # FIXME: generate the keypair
    #     keypair = params.generate_keypair()
    #
    #     # create the trustee
    #     trustee = Trustee(election = self)
    #     trustee.uuid = str(election_uuid.uuid4())
    #     trustee.name = settings.DEFAULT_FROM_NAME
    #     trustee.email = settings.DEFAULT_FROM_EMAIL
    #     trustee.public_key = keypair.pk
    #     trustee.secret_key = keypair.sk
    #
    #     # FIXME: is this at the right level of abstraction?
    #     trustee.public_key_hash = datatypes.LDObject.instantiate(trustee.public_key,
    #                                                              datatype = 'legacy/EGPublicKey').hash
    #
    #     trustee.pok = trustee.secret_key.prove_sk(algs.DLog_challenge_generator)
    #
    #     trustee.save()

    def get_helios_trustee(self):
        trustees_with_sk = self.trustee_set.exclude(secret_key = None)
        if len(trustees_with_sk) > 0:
            return trustees_with_sk[0]
        else:
            return None

    def has_helios_trustee(self):
        return self.get_helios_trustee() != None

    # def helios_trustee_decrypt(self):
    #     tally = self.encrypted_tally
    #     tally.init_election(self)
    #
    #     trustee = self.get_helios_trustee()
    #     factors, proof = tally.decryption_factors_and_proofs(trustee.secret_key)
    #
    #     trustee.decryption_factors = factors
    #     trustee.decryption_proofs = proof
    #     trustee.save()


class Voter(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    user = models.ForeignKey(User, null = True, on_delete = models.CASCADE)
    #uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    uuid=models.CharField(max_length = 200, null = True)
    #voter_login_code = models.CharField(max_length = 100, null = True) #cod primit prin care se logheaza
    #vote_hash = models.CharField(max_length = 200, null = True)
    #cast_at = models.DateTimeField(auto_now_add = False, null = True)


#     @property
#     def get_user(self):
#         return User.objects.filter(email=self.voter_email)
#
#     @property
#     def voter_id(self):
#         return self.get_user().id
#
    @property
    def voter_id_hash(self):
        if self.voter_login_id:
            # for backwards compatibility with v3.0, and since it doesn't matter
            # too much if we hash the email or the unique login ID here.
            value_to_hash = self.voter_login_id
        else:
            value_to_hash = self.voter_id

        try:
            return utils_functions.hash_b64(value_to_hash)
        except:
            try:
                return utils_functions.hash_b64(value_to_hash.encode('latin-1'))
            except:
                return utils_functions.hash_b64(value_to_hash.encode('utf-8'))

#
#     def generate_voter_login_code(self, length = 10):
#         if self.voter_login_code:
#             raise Exception("password already exists")
#
#         self.voter_login_code = utils_functions.random_string(length,
#                                                               alphabet = 'abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')


class Choice(models.Model):  # 1 Choice apartine unei singure Election
    election = models.ForeignKey(Election,
                                 on_delete = models.CASCADE)  # sterg Election => se sterg toate Choice pe care le are
    choice_text = models.CharField(max_length = 200)
    # votes = models.IntegerField(default=0)
    #choice_hash = models.CharField(max_length = 100, null = True, unique = True)
    # hash scurt pe care sa il pun in url
    #choice_tinyhash = models.CharField(max_length = 50, null = True, unique = True)

    # voter = models.ForeignKey(Voter, on_delete = models.CASCADE)

    def __str__(self):
        return self.choice_text

    @property
    def num_votes(self):
        return self.vote_set.count()  # nr de voturi primite de aceasta choice


class Vote(models.Model):  # ca un user sa NU poata vota de mai multe ori
    # models.PROTECT = daca sterg P(parinte), iar acesta are copii, nu il pot sterge (pe P)
    voter = models.OneToOneField(Voter, on_delete = models.CASCADE)  # sterg User=> sterg toate Votes asociate
    election = models.ForeignKey(Election, on_delete = models.CASCADE)  # sterg Election=> sterg toate Votes asociate
    choice = models.ForeignKey(Choice, on_delete = models.CASCADE)  # sterg Choice=> sterg toate Votes asociate

    vote_hash = models.CharField(max_length = 200, null = True)
    vote_tinyhash = models.CharField(max_length = 50, null = True, unique = True)
    cast_at = models.DateTimeField(auto_now_add = True, null = True)

    verified_at = models.DateTimeField(null = True)
    invalidated_at = models.DateTimeField(null = True)

    alpha = models.IntegerField(default = 0)
    beta = models.IntegerField(default = 0)

    c1 = models.IntegerField(default=0)
    c2 = models.IntegerField(default = 0)
    # uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    # user_uuid = models.CharField(max_length = 50)#user uuid

    def set_tinyhash(self):
        """
        find a tiny version of the hash for a URL slug.
        """
        safe_hash = self.vote_hash
        for c in ['/', '+']:
            safe_hash = safe_hash.replace(c, '')

        length = 8
        while True:
            vote_tinyhash = safe_hash[:length]
            if Vote.objects.filter(vote_tinyhash = vote_tinyhash).count() == 0:
                break
            length += 1
        self.vote_tinyhash = vote_tinyhash

    # def save(self, *args, **kwargs):
    #     """
    #     override this just to get a hook
    #     """
    #     # not saved yet? then we generate a tiny hash
    #     if not self.vote_tinyhash:
    #         self.set_tinyhash()
    #
    #     super(Vote, self).save(*args, **kwargs)


class AuditedBallot(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)
    raw_vote = models.TextField(null = True)
    vote_hash = models.CharField(max_length = 200, null = True)
    added_at = models.DateTimeField(auto_now_add = True, null = True)

    # @classmethod
    # def get(cls, election, vote_hash):
    #     return cls.objects.get(election = election, vote_hash = vote_hash)


class Trustee(models.Model):
    election = models.ForeignKey(Election, on_delete = models.CASCADE)

    uuid = models.CharField(max_length = 50, null = True)
    name = models.CharField(max_length = 200, null = True)
    secret = models.CharField(max_length = 100, null = True)

    # public key
    public_key = models.CharField(max_length = 200, null = True)
    # LDObjectField(type_hint = 'legacy/EGPublicKey',null = True)
    public_key_hash = models.CharField(max_length = 100, null = True)

    # secret key
    # if the secret key is present, this means
    # Helios is playing the role of the trustee.
    secret_key = models.CharField(max_length = 200, null = True)
    # LDObjectField(type_hint = 'legacy/EGSecretKey',null = True)

    # proof of knowledge of secret key
    pok = models.CharField(max_length = 200, null = True)

    # LDObjectField(type_hint = 'legacy/DLogProof',null = True)

    # decryption factors
    # decryption_factors = LDObjectField(type_hint = datatypes.arrayOf(datatypes.arrayOf('core/BigInteger')),
    #                                    null = True)
    #
    # decryption_proofs = LDObjectField(type_hint = datatypes.arrayOf(datatypes.arrayOf('legacy/EGZKProof')),
    #                                   null = True)

    class Meta:
        unique_together = (('election', 'email'))
        app_label = 'helios'

    def save(self, *args, **kwargs):
        """
        override this just to get a hook
        """
        # not saved yet?
        if not self.secret:
            self.secret = utils_functions.random_string(12)

        super(Trustee, self).save(*args, **kwargs)

    @classmethod
    def get_by_election(cls, election):
        return cls.objects.filter(election = election)

    # @classmethod
    # def get_by_uuid(cls, uuid):
    #     return cls.objects.get(uuid = uuid)
    #
    # @classmethod
    # def get_by_election_and_uuid(cls, election, uuid):
    #     return cls.objects.get(election = election, uuid = uuid)

    @classmethod
    def get_by_election_and_email(cls, election, email):
        try:
            return cls.objects.get(election = election, email = email)
        except cls.DoesNotExist:
            return None

    # def verify_decryption_proofs(self):
    #     """
    #     verify that the decryption proofs match the tally for the election
    #     """
    #     # verify_decryption_proofs(self, decryption_factors, decryption_proofs, public_key, challenge_generator):
    #     return self.election.encrypted_tally.verify_decryption_proofs(self.decryption_factors, self.decryption_proofs,
    #                                                                   self.public_key,
    #                                                                   algs.EG_fiatshamir_challenge_generator)
