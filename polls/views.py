from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from polls.models import Election, Choice, Vote, ValidVote, Trustee
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from polls.forms import ElectionForm, EditElectionForm, ChoiceForm
from polls.crypto import functiiUtile, algoritmi, Vote_Trustees_check
import hashlib


# !!! Ce trimit in context este vizibil in template(.html) !!!!!


def HomeView(request):
    return render(request, 'polls/home.html',{})


@login_required
def IndexView(request):
    is_allowed = request.user.is_staff or request.user.is_superuser
    searchContent = ""  # ce contine initial search-ul
    #user_current = functiiUtile.get_user_type(request)  # uuid

    if functiiUtile.is_Admin_or_Staff(request):
        polls = Election.objects.all().order_by('start_date')  # Admin ul sau Stuff ul vede toate polls
    else:
        # cele active care au start_date inainte de prezentul meu
        polls = Election.objects.filter(isActive = True).filter(start_date__lte = timezone.now()).order_by(
            '-start_date')

    if 'title' in request.GET:  # ordonare crescator dupa titlu
        polls = polls.order_by('election_title')

    if 'creator' in request.GET: #elections pe care le-a creat
        polls=polls.filter(owner=request.user)

    if 'searchElection' in request.GET:
        searchContent = request.GET['searchElection']  # ce a tastat User ul in search
        # headline(adica election_title) + __ + metoda folosita(adica icontains)
        polls = polls.filter(election_title__icontains = searchContent)

    prezent=timezone.now()
    # asezare in pagina (cate 4 polls)
    paginator = Paginator(polls, 4)
    page = request.GET.get('page', 1)
    try:
        polls_paginated = paginator.page(page)
    except PageNotAnInteger:
        polls_paginated = paginator.page(1)
    except EmptyPage:
        polls_paginated = paginator.page(paginator.num_pages)

    # pentu ca ordonarea alfabetica sa fie activa pe toate paginile (at cand A-Z este galben(warning))
    get_dict_copy = request.GET.copy()
    # ca sa pot pune in ruta &{{params}} in index.html
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

    context = {
        'polls': polls_paginated, 'params': params, 'searchContent': searchContent, 'is_allowed': is_allowed,
        'prezent':prezent
        }
    return render(request, 'polls/index.html', context)


@login_required
def AddElectionView(request):
    if not functiiUtile.is_Admin_or_Staff(request):  # doar cei din stuff pot crea o noua Election
        messages.error(request, 'You are not allowed to add an election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        form = ElectionForm(request.POST)
        if form.is_valid():  # in documentatie la forms-> save method
            new_election = form.save(commit = False)  # NU salvez inca in BD
            new_election.owner = request.user

            if new_election.start_date < timezone.now():
                messages.error(request, 'Start date can not be in the past!!',
                               extra_tags = 'alert alert-danger alert-dismissible fade show')
                context = {'form': form}  # 'form' este keyword pe care il folosesc in html
                return render(request, 'polls/add.html', context)

            if new_election.end_date <= new_election.start_date:
                messages.error(request, 'End date can not be smaller or equal to start date!!',
                               extra_tags = 'alert alert-danger alert-dismissible fade show')
                context = {'form': form}
                return render(request, 'polls/add.html', context)

            p, q, g = algoritmi.generateEG_p_q_g()
            public_key, secret_key = algoritmi.generateEG_pk_sk(p, q, g)
            new_election.p = p

            new_election.q = q
            new_election.g = g
            new_election.public_key = public_key
            new_election.secret_key = secret_key
            new_election.modified_at = timezone.now()
            new_election = form.save()  # salvez in BD
            new_election.save()

            new_choice1 = Choice(
                election = new_election,
                choice_text = form.cleaned_data['choice1']
                ).save()
            new_choice2 = Choice(
                election = new_election,
                choice_text = form.cleaned_data['choice2']  # choice2 din forms.py
                ).save()
            # creez Trustee1

            posk = algoritmi.ZKProofIACR_Trustee_verify_sk(p, q, q, secret_key, public_key)
            name = "Trustee1"
            new_trustee1 = Trustee(election = new_election, public_key = public_key, secret_key = secret_key,
                                   posk = posk, name = name)
            new_trustee1.save()
            # creez Trustee2
            public_key_t2, secret_key_t2 = algoritmi.generateEG_pk_sk(p, q, g)
            posk2 = algoritmi.ZKProofIACR_Trustee_verify_sk(p, q, q, secret_key_t2, public_key_t2)
            name2 = "Trustee2"
            new_trustee2 = Trustee(election = new_election, public_key = public_key_t2, secret_key = secret_key_t2,
                                   posk = posk2, name = name2)
            new_trustee2.save()

            # alert alert-success este din Bootstrap
            messages.success(request, 'Election was successfully added!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:index')
    else:
        form = ElectionForm()
    context = {'form': form}  # 'form' este keyword pe care il folosesc in html
    return render(request, 'polls/add.html', context)


@login_required()
def EditElectionView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)

    if not functiiUtile.can_edit_Election(request, poll):
        messages.error(request, 'You are not allowed to edit this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        form = EditElectionForm(request.POST, instance = poll)
        if form.is_valid():

            if poll.start_date < timezone.now():
                messages.error(request, 'Start date can not be in the past!!',
                               extra_tags = 'alert alert-danger alert-dismissible fade show')
                return redirect('polls:edit', poll_id = poll_id)

            if poll.end_date <= poll.start_date:
                messages.error(request, 'End date can not be smaller or equal to start date!!',
                               extra_tags = 'alert alert-danger alert-dismissible fade show')
                return redirect('polls:edit', poll_id = poll_id)

            poll.modified_at = timezone.now()
            poll.save()
            form.save()
            messages.success(request, 'Election was successfully modified!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:index')

    else:
        form = EditElectionForm(instance = poll)
        # pun {'form':form} ca sa imi afiseze fields din form; 'poll':poll pentru a adauga choice
    return render(request, 'polls/edit.html', {'form': form, 'poll': poll})


@login_required
def DeleteElectionView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)
    if not functiiUtile.can_edit_Election(request, poll):
        messages.error(request, 'You are not allowed to delete this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        poll.delete()
        messages.success(request, 'Election deleted successfully',
                         extra_tags = 'alert alert-success alert-dismissible fade show')
        return redirect('polls:index')

    return render(request, 'polls/delete.html', {'poll': poll})


@login_required
def AddChoiceView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)
    if not functiiUtile.can_edit_Election(request, poll):
        messages.error(request, 'You are not allowed to add a choice!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        form = ChoiceForm(request.POST)
        if form.is_valid():

            new_choice = form.save(commit = False)
            # daca deja exista aceasta optiune => EROARE!(nu mai poate fi adaugata din nou)
            chs = Choice.objects.filter(election = poll)
            # folosesc __iexact pentru a face abstractie de upper/lower case (ex: meRE1=MERE1)
            if Choice.objects.filter(election = poll).filter(choice_text__iexact = new_choice.choice_text):
                messages.error(request, 'This choice already exists in current election!',
                               extra_tags = 'alert alert-danger alert-dismissible fade show')
                return redirect('polls:edit', poll_id = poll.id)

            new_choice.election = poll
            poll.save()
            poll.modified_at = timezone.now()
            new_choice.save()
            messages.success(request, 'Choice added successfully !',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll_id = poll.id)
    else:
        form = ChoiceForm()
    return render(request, 'polls/add_choice.html',
                  {'form': form})  # pun {'form':form} ca sa imi afiseze fields din form


@login_required
def EditChoiceView(request, choice_id):
    choice = get_object_or_404(Choice, id = choice_id)
    poll = get_object_or_404(Election, id = choice.election.id)
    if not functiiUtile.can_edit_Election(request, poll):
        messages.error(request, 'You are not allowed to edit this choice!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        form = ChoiceForm(request.POST, instance = choice)
        if form.is_valid():

            # daca deja exista aceasta optiune => EROARE!(nu mai poate fi adaugata din nou)
            chs = Choice.objects.filter(election = poll)
            # folosesc __iexact pentru a face abstractie de upper/lower case (ex: meRE1=MERE1)
            if Choice.objects.filter(election = poll).filter(choice_text__iexact = choice.choice_text):
                messages.error(request, 'This choice already exists in current election!',
                               extra_tags = 'alert alert-danger alert-dismissible fade show')
                return redirect('polls:edit', poll_id = poll.id)

            poll.modified_at = timezone.now()
            poll.save()
            form.save()  # editez choice care exista deja
            messages.success(request, 'Choice edited successfully !',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll_id = poll.id)
    else:
        form = ChoiceForm(instance = choice)
        # pasez choice ca sa o accesez
    return render(request, 'polls/add_choice.html', {'form': form, 'edit_mode': True, 'choice': choice})


@login_required
def DeleteChoiceView(request, choice_id):
    choice = get_object_or_404(Choice, id = choice_id)
    poll = get_object_or_404(Election, id = choice.election.id)
    choices_number = Choice.objects.filter(election = poll).count()

    if (choices_number > 2):
        if not functiiUtile.can_edit_Election(request, poll):
            messages.error(request, 'You are not allowed to delete this choice!',
                           extra_tags = 'alert alert-danger alert-dismissible fade show')
            return redirect('polls:index')

        if request.method == "POST":
            poll.modified_at = timezone.now()
            poll.save()
            choice.delete()
            messages.success(request, 'Choice deleted successfully!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:edit', poll_id = poll.id)

    else:
        messages.error(request, 'Election should have at least 2 choices!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:edit', poll_id = poll.id)

    return render(request, 'polls/delete_choice.html', {'choice': choice})


@login_required
def DetailView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)

    is_first_vote_for_this_election = poll.is_first_vote_for_this_election(request.user)
    # daca NU este publicata si este User => este vizibila doar pentru Admin/Saff
    if not functiiUtile.can_see_DetailView(request, poll):
        messages.error(request, 'You are not allowed to see this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    context = {'election': poll, 'is_first_vote_for_this_election': is_first_vote_for_this_election}
    return render(request, 'polls/detail.html', context)


@login_required
def VotesIndexView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)
    verified_votes = ValidVote.objects.filter(election = poll).order_by('-added_at')
    exists_votes = True
    if not verified_votes.exists():
        exists_votes = False  # inca nu sunt voturi

    votes_number = verified_votes.count()

    searchContent = ""
    if 'searchCastedVote' in request.GET:
        searchContent = request.GET['searchCastedVote']  # ce a tastat User ul in search
        # headline(adica election_title) + __ + metoda folosita(adica icontains)
        verified_votes = verified_votes.filter(vote_hash__icontains = searchContent)

    # cate 4 votes pe pagina
    paginator = Paginator(verified_votes, 4)
    page = request.GET.get('page', 1)

    try:
        verified_votes_paginated = paginator.page(page)
    except PageNotAnInteger:
        verified_votes_paginated = paginator.page(1)
    except EmptyPage:
        verified_votes_paginated = paginator.page(paginator.num_pages)

    context = {
        'verified_votes': verified_votes_paginated, 'poll': poll, 'exists_votes': exists_votes,
        'votes_number': votes_number, 'searchContent': searchContent,
        }
    return render(request, 'polls/votes_index.html', context)


@login_required
def ResultsView(request, poll_id):
    ok = 0  # inca nu am sters Votes
    poll = get_object_or_404(Election, id = poll_id)
    if not poll.can_see_results:
        messages.error(request, 'Election is not finished! You can not see the results!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    # is_first_vote_for_this_election = poll.is_first_vote_for_this_election(request.user)
    results, max_votes = poll.get_results_dict()
    print('rezultate=',results)
    winners = []
    result_names = ""
    for choice in poll.choice_set.all():
        if choice.num_votes == max_votes:
            winners.append(choice.choice_text)
            result_names = result_names + choice.choice_text + "  "

    number_of_winners = len(winners)
    ok = 0  # este 0 daca am mai multi castigatori
    if number_of_winners == 1:
        ok = 1  # este 1 daca am 1 singur castigator

    if(ok==1):#1 castigator
        poll.result = result_names
    else:
        poll.result="Remiza: "+result_names

    poll.result_released_at = timezone.now()
    poll.save()

    context = {'election': poll, 'results': results, 'winners': winners, 'ok': ok}
    return render(request, 'polls/results.html', context)


@login_required
def vote(request, poll_id):
    election = get_object_or_404(Election, pk = poll_id)
    # daca inca nu a inceput, s-a sfarsit sau nu este publica => NU poate vota

    if not election.isActive:
        messages.error(request, 'Election is not published! You can not vote!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)
    if election.can_see_results:
        messages.error(request, 'Election is closed! You can not vote anymore!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:results', poll_id = poll_id)

    if election.start_date > timezone.now():
        messages.error(request, 'Election is not opened yet! You can not vote!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)

    is_first_vote_for_this_election=election.is_first_vote_for_this_election(request.user)
    if not is_first_vote_for_this_election:
        messages.error(request, 'You have already voted on this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)

    choice_id = request.POST.get('choice')
    if not choice_id:
        messages.error(request, 'You must select a choice',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)
    else:

        cast_at = timezone.now()
        choice = Choice.objects.get(id = choice_id)

        if int(choice_id) % int(election.p) ==0:
            m_modulo= (int(choice_id) +1) % int(election.p) #pun +1 pt ca nu gasea inversul lui 0 in grup
        else:
            m_modulo=int(choice_id )% int(election.p)

        m = int(hashlib.sha256(str(m_modulo).encode()).hexdigest(), 16)
        # pentru fiecare vot nou se geneereaza o pereche (pk,sk)
        pk_vote, sk_vote = algoritmi.generateEG_pk_sk(election.p, election.q, election.g)
        alpha_vote, beta_vote, randomness_vote = algoritmi.generateEG_alpha_beta_randomness(election.p, election.q,
                                                                                            election.g, sk_vote,
                                                                                            pk_vote, m)
        validare_Helios = algoritmi.ChaumPederson_proof_that_alpha_beta_encodes_m(election.p, election.q,
                                                                                  election.g,
                                                                                  pk_vote, m, alpha_vote,
                                                                                  beta_vote, randomness_vote)

        new_vote = Vote(voter = request.user, election = election, cast_at = cast_at)
        new_vote.save()

        trustee1 = get_object_or_404(Trustee, name = 'Trustee1', election = election)
        validare_trustee1 = Vote_Trustees_check.Trustee_validate_vote(election.p, election.q, election.g, sk_vote,
                                                                      pk_vote,
                                                                      trustee1.secret_key, trustee1.public_key,
                                                                      alpha_vote, beta_vote, randomness_vote, m)

        trustee2 = get_object_or_404(Trustee, name = 'Trustee2', election = election)
        validare_trustee2 = Vote_Trustees_check.Trustee_validate_vote(election.p, election.q, election.g, sk_vote,
                                                                      pk_vote,
                                                                      trustee2.secret_key, trustee2.public_key,
                                                                      alpha_vote, beta_vote, randomness_vote, m)
        print('trustee1=', trustee1)
        print('trustee2=', trustee2)

        ok = False
        verified_at = timezone.now()
        new_vote.verified_at = verified_at
        new_vote.save()
        print('validare Helios=', validare_Helios, 'validare_trustee1=', validare_trustee1,
              'validare_trustee2=', validare_trustee2, 'trustee1.posk =', trustee1.posk, 'trustee2.posk=',
              trustee2.posk)
        if validare_Helios and validare_trustee1 and validare_trustee2:  # and trustee1.posk and trustee2.posk:

            choice.num_votes=choice.num_votes+1#creste nr de voturi pentru aceasta choice
            choice.save()

            vote_hash_ = hashlib.sha256(
                (str(sk_vote) + ',' + str(alpha_vote) + ',' + str(beta_vote) + ',' + str(randomness_vote) + ',' +
                 str(election.election_title) + ',' + str(election.id)).encode()).hexdigest()

            verified_vote = ValidVote(election = election,text_vote = choice.choice_text,
                                      vote_hash = vote_hash_, added_at = timezone.now())
            verified_vote.save()

            messages.success(request, 'You successfully voted for {} in election {}! Details about your vote: '
                                      'vote_hash = {}, sk={}, alpha= {}, beta= {}, randomness= {} '
                             .format(choice.choice_text,election.election_title, verified_vote.vote_hash,
                                     sk_vote,alpha_vote, beta_vote,
                                     randomness_vote),
                             extra_tags = 'alert alert-success alert-dismissible fade show')

            messages.success(request,'Please apply SHA-256(sk,alpha,beta,randomness,{},{}) to verify your vote_hash. '
                                        'Please write down this vote_hash in order to find it in Casted Votes.'
                             .format(election.election_title, election.id),
                             extra_tags = 'alert alert-success alert-dismissible fade show')

            ok = True
        else:
            invalidated_at = timezone.now()
            messages.error(request,
                           'Something went wrong! Your vote has NOT been casted!'
                           'Please retry! If thprme problem persists, please contact us on voote5@voote5.com!',
                           extra_tags = 'alert alert-danger alert-dismissible fade show')
            new_vote.invalidated_at = invalidated_at
            new_vote.save()
            return redirect('polls:detail', poll_id = poll_id)

    #return render(request,'polls:index',{'is_first_vote_for_this_election':is_first_vote_for_this_election})
    return redirect("polls:detail", poll_id = poll_id)
