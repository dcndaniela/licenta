from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from polls.models import Election, Choice, Vote, Voter, AuditedBallot
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from polls.forms import ElectionForm, EditElectionForm, ChoiceForm
from polls import eg, algoritmi
import hashlib
from random import randint
import math




# !!! Ce trimit in context este vizibil in template(.html) !!!!!

#ELGAMAL_PARAMS = elgamal.Cryptosystem()


@login_required
def IndexView(request):
    is_allowed = request.user.is_staff
    searchContent=""#ce contine initial search-ul
    user_current=request.user.alias #uuid
    #user_current="User"+user_current_alias[0:8]

    if request.user.is_staff:
         polls = Election.objects.all().order_by('start_date') #Admin ul vede toate polls
    else:
        # cele activate care au start_date inainte de prezentul meu
        polls = Election.objects.filter(isActive = True).filter(start_date__lte = timezone.now()).order_by('-start_date')

    if 'title' in request.GET:#ordonare crescator dupa titlu
        polls=polls.order_by('election_title')

    if 'searchElection' in request.GET:
        searchContent=request.GET['searchElection'] #ce a tastat User ul in search
        #headline(adica election_title) + __ + metoda folosita(adica icontains)
        polls=polls.filter(election_title__icontains=searchContent)

    paginator = Paginator(polls, 4)
    page = request.GET.get('page', 1)

    try:
        polls_paginated = paginator.page(page)
    except PageNotAnInteger:
        polls_paginated = paginator.page(1)
    except EmptyPage:
        polls_paginated = paginator.page(paginator.num_pages)

    #pentu ca ordonarea alfabetica sa fie activa pe toate paginile (at cand A-Z este galben(warning))
    get_dict_copy=request.GET.copy()
    # ca sa pot pune in ruta &{{params}} in index.html
    params=get_dict_copy.pop('page',True) and get_dict_copy.urlencode()

    context = {'polls': polls_paginated, 'params':params,'searchContent':searchContent,'is_allowed':is_allowed,
               'user_current':user_current}
    return render(request, 'polls/index.html',context)
    #return redirect('polls:index')


@login_required
def AddElectionView(request):
    if not request.user.is_staff: #doar cei din stuff pot crea o noua Election
        messages.error(request, 'You are not allowed to add an election!',
                         extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method =="POST":
        form=ElectionForm(request.POST)
        if form.is_valid(): #in documentatiela forms-> save method
            new_election = form.save(commit=False)# NU salvez inca in BD
            #new_election.pub_date=datetime.datetime.now()
            new_election.owner=request.user
            pk,sk = eg.generate_keys()
            new_election.public_key = pk
            print('public key=',pk)
            #print('sk view=',randint(1, 46))
            new_election.private_key = sk
            new_election.modified_at = timezone.now()
            #new_election = form.save()  # salvez in BD
            new_election.save()
            new_election.election_hash = hashlib.sha224((str(new_election.election_title)
                                                         + str(new_election.public_key)).encode()).hexdigest()
            new_election.save()

            new_choice1=Choice(
                election=new_election,
                choice_text=form.cleaned_data['choice1']
                ).save()
            new_choice2 = Choice(
                election = new_election,
                choice_text = form.cleaned_data['choice2'] #choice2 din forms.py
                ).save()
            #alert alert-success este din Bootstrap
            messages.success(request,'Election was successfully added!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:index')
    else:
        form=ElectionForm()
    context={'form':form} # 'form' este keyword pe care il folosesc in html
    return render(request,'polls/add.html',context)

@login_required()
def EditElectionView(request,poll_id):
    poll=get_object_or_404(Election,id=poll_id)
    if request.user != poll.owner or (not request.user.is_staff) or (not poll.has_not_started):
        messages.error(request, 'You are not allowed to edit this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method=="POST":
        form= EditElectionForm(request.POST,instance = poll)
        if form.is_valid():
            poll.modified_at = timezone.now()
            poll.save()
            form.save()
            messages.success(request, 'Election was successfully modified!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:index')

    else:
        form= EditElectionForm(instance = poll)
        # pun {'form':form} ca sa imi afiseze fields din form; 'poll':poll pentru a adauga choice
    return render(request,'polls/edit.html',{'form':form, 'poll':poll})


@login_required
def DeleteElectionView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)
    if request.user != poll.owner or (not request.user.is_staff) or (not poll.has_not_started):
        messages.error(request, 'You are not allowed to delete this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        poll.delete()
        messages.success(request,'Election deleted successfully',
            extra_tags = 'alert alert-success alert-dismissible fade show'
            )
        return redirect('polls:index')
    return render(request, 'polls/delete.html', {'poll': poll})


@login_required
def AddChoiceView(request, poll_id):
    poll=get_object_or_404(Election,id=poll_id)
    if request.user != poll.owner or (not request.user.is_staff) or (not poll.has_not_started):
        messages.error(request, 'You are not allowed to add a choice!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method=="POST":
        form= ChoiceForm(request.POST)
        if form.is_valid():
            poll.modified_at = timezone.now()
            poll.save()
            new_choice=form.save(commit = False)
            new_choice.election=poll
            new_choice.save()
            messages.success(request, 'Choice added successfully !',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:index')
    else:
        form= ChoiceForm()
    return render(request,'polls/add_choice.html',{'form':form})# pun {'form':form} ca sa imi afiseze fields din form


@login_required
def EditChoiceView(request,choice_id):
    choice=get_object_or_404(Choice,id=choice_id)
    poll=get_object_or_404(Election,id=choice.election.id)
    if request.user != poll.owner or (not request.user.is_staff) or (not poll.has_not_started):
        messages.error(request, 'You are not allowed to edit this choice!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method=="POST":
        form= ChoiceForm(request.POST,instance = choice)
        if form.is_valid():
            poll.modified_at = timezone.now()
            poll.save()
            form.save() #editez choice care exista deja
            messages.success(request, 'Choice edited successfully !',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:index')
    else:
        form= ChoiceForm(instance = choice)
        # pasez choice ca sa o accesez
    return render(request, 'polls/add_choice.html', {'form':form, 'edit_mode': True, 'choice':choice})


@login_required
def DeleteChoiceView(request,choice_id):
    choice = get_object_or_404(Choice, id = choice_id)
    poll = get_object_or_404(Election, id = choice.election.id)
    if request.user != poll.owner or (not request.user.is_staff) or (not poll.has_not_started):
        messages.error(request, 'You are not allowed to delete tis choice!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    if request.method == "POST":
        poll.modified_at = timezone.now()
        poll.save()
        choice.delete()
        messages.success(request,'Choice deleted successfully!',
        extra_tags = 'alert alert-success alert-dismissible fade show'
        )
        return redirect('polls:index')
        #return redirect('polls:edit', choice_id=choice.id)
    return render(request, 'polls/delete_choice.html', {'choice': choice})


@login_required
def DetailView(request,poll_id):
    poll = get_object_or_404(Election, id=poll_id)

    #user_can_vote=poll.user_can_vote(request.user)
    # daca NU este activa sau inca nu a fost publicata, este vizibila doar pentru Admin
    if not poll.isActive or poll.start_date>timezone.now() :
        if not request.user.is_superuser:
            return redirect('polls:index')

    #context={'election': poll,'user_can_vote':user_can_vote}
    context = {'election': poll}
    return render(request, 'polls/detail.html', context)


@login_required
def VotesIndexView(request, poll_id):
    poll = get_object_or_404(Election, id = poll_id)
    audited_ballots= AuditedBallot.objects.filter(election=poll).order_by('-added_at')

    # cate 4 votes pe pagina
    paginator = Paginator(audited_ballots, 4)
    page = request.GET.get('page', 1)

    try:
        audited_ballots_paginated = paginator.page(page)
    except PageNotAnInteger:
        audited_ballots_paginated = paginator.page(1)
    except EmptyPage:
        audited_ballots_paginated = paginator.page(paginator.num_pages)

    context={'audited_ballots': audited_ballots_paginated,'poll': poll}
    return render(request,'polls/votes_index.html',context)


@login_required
def ResultsView(request,poll_id):
    ok=0#inca nu am sters Votes
    poll = get_object_or_404(Election, id = poll_id)

    if not poll.can_see_results:
        messages.error(request, 'Election is not finished! You can not see the results!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    #user_can_vote = poll.user_can_vote(request.user)
    results=poll.get_results_dict()
    print (results)
    # for key in results:
    #     if key=='num_votes':
    #         if results[]
    # if ok ==1:
    #     return redirect('polls:votes_index',poll_id = poll_id)
    # Vote.objects.filter( election = poll).delete()#sterg voturile at cand se publica rezultatul(le salvez doar in AuditedBallot
    context = {'election': poll, 'results':results }
    ok=1
    return render(request, 'polls/results.html', context)


@login_required
def vote(request, poll_id):
    election = get_object_or_404(Election, pk = poll_id)
    # daca inca nu a inceput, s-a sfarsit sau nu este pubica => NU poate vota
    if election.start_date>timezone.now() or election.isActive==False:
        messages.error(request, 'Election is not opened yet!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')
    if election.end_date<timezone.now():
        messages.error(request, 'Election is closed!You can not vote anymore!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:results', poll_id = poll_id)

    # user_can_vote=election.user_can_vote(request.user)
    # if not user_can_vote:
    #     messages.error(request, 'You have already voted on this election!',
    #                    extra_tags = 'alert alert-danger alert-dismissible fade show')
    #     return redirect('polls:detail', poll_id = poll_id)

    choice_id=request.POST.get('choice')
    if choice_id:
        print(choice_id)
        #user_uuid=str(uuid.uuid4())
        cast_at=timezone.now()
        choice=Choice.objects.get(id=choice_id)
        voter=Voter(election=election, user=request.user)
        voter.save()

        alpha, beta, r= eg.encrypt(int(election.public_key),int(choice_id))
        vote_hash_=hashlib.sha224((str(voter.election.election_title)+str(alpha)+","+str(beta)).encode()).hexdigest()
        print('alpha=',alpha,'\n','beta=',beta,'\n','randomness=',r,'\n','vote hash=',vote_hash_,
              '\n','election_PK=',election.public_key)

        v_election_hash = hashlib.sha224(
            (str(election.election_title) + str(election.public_key)).encode()).hexdigest()
        print('v_election_hash=',v_election_hash,'\n','election_hash=',election.election_hash)
        if not (election.election_hash == v_election_hash):
            messages.error(request, 'Something went wrong! Please contact us on vootes@vootes.com!',
                           extra_tags = 'alert alert-danger alert-dismissible fade show')
            return redirect('polls:detail', poll_id = poll_id)

        # if not algoritmi.verify_alpha_and_beta(alpha,beta,r,election.public_key,choice_id):
        #     messages.error(request, 'Something went wrong! Please contact us on vootes@vootes.com!',
        #                    extra_tags = 'alert alert-danger alert-dismissible fade show')
        #     return redirect('polls:detail', poll_id = poll_id)

        new_vote=Vote(voter=voter, election=election, choice=choice,cast_at=cast_at,vote_hash=vote_hash_,
                      alpha=alpha,beta=beta)
        new_vote.set_tinyhash()
        new_vote.save()
        #print("tinyhash="+new_vote.vote_tinyhash)
        audited_ballot=AuditedBallot(election=election,raw_vote=choice.choice_text,
                                     vote_hash=vote_hash_,added_at=timezone.now())
        audited_ballot.save()

        messages.success(request,'Your vote has been added successfully: choice= {} vote_hash = {},alpha= {} ,beta= {},randomness= {} '
                      .format(choice.choice_text,new_vote.vote_hash,alpha,beta,r),
                       extra_tags = 'alert alert-success alert-dismissible fade show')
        #print(choice)
    else:
        messages.error(request,'You must select a choice',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)
    #return render(request,'polls:index',{'user_can_vote':user_can_vote})
    return redirect("polls:detail", poll_id = poll_id)
