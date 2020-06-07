import uuid as uuid
from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from polls.models import Election, Choice, Vote, Voter
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from polls.forms import ElectionForm, EditElectionForm, ChoiceForm
from polls.crypto import elgamal

# !!! Ce trimit in context este vizibil in template(.html) !!!!!

#ELGAMAL_PARAMS = elgamal.Cryptosystem()


p = 16328632084933010002384055033805457329601614771185955389739167309086214800406465799038583634953752941675645562182498120750264980492381375579367675648771293800310370964745767014243638518442553823973482995267304044326777047662957480269391322789378384619428596446446984694306187644767462460965622580087564339212631775817895958409016676398975671266179637898557687317076177218843233150695157881061257053019133078545928983562221396313169622475509818442661047018436264806901023966236718367204710755935899013750306107738002364137917426595737403871114187750804346564731250609196846638183903982387884578266136503697493474682071
q = 61329566248342901292543872769978950870633559608669337131139375508370458778917
g = 14887492224963187634282421537186040801304008017743492304481737382571933937568724473847106029915040150784031882206090286938661464458896494215273989547889201144857352611058572236578734319505128042602372864570426550855201448111746579871811249114781674309062693442442368697449970648232621880001709535143047913661432883287150003429802392229361583608686643243349727791976247247948618930423866180410558458272606627111270040091203073580238905303994472202930783207472394578498507764703191288249547659899997131166130259700604433891232298182348403175947450284433411265966789131024573629546048637848902243503970966798589660808533


@login_required
def HomeView(request):
    return render(request,'polls/home.html')

@login_required
def IndexView(request):
    is_allowed = request.user.is_staff
    searchContent=""#ce contine initial search-ul

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

    context = {'polls': polls_paginated, 'params':params,'searchContent':searchContent,'is_allowed':is_allowed}
    return render(request, 'polls/index.html',context)

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
            new_election=form.save()#salvez in BD
            #new_poll = form.save(commit=False)  # NU salvez in BD; dupa ce modific apelez manual: new_poll.save()
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
        choice.delete()
        messages.success(request,'Choice deleted successfully',
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
def ResultsView(request,poll_id):

    poll = get_object_or_404(Election, id = poll_id)

    if not poll.can_see_results:
        messages.error(request, 'Election is not finished! You can not see the results!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')

    #user_can_vote = poll.user_can_vote(request.user)
    results=poll.get_results_dict()
    context = {'election': poll, 'results':results }
    return render(request, 'polls/results.html', context)


@login_required
def vote(request, poll_id):
    election = get_object_or_404(Election, pk = poll_id)
    if election.start_date>timezone.now():
        messages.error(request, 'Election is not opened yet!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:index')
    if election.end_date<timezone.now():
        messages.error(request, 'Election is closed!You can not vote anymore!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:results', poll_id = poll_id)

    user_can_vote=election.user_can_vote(request.user)
    if not user_can_vote:
        messages.error(request, 'You have already voted on this election!',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)

    choice_id=request.POST.get('choice')
    if choice_id:
        #user_uuid=str(uuid.uuid4())
        cast_at=timezone.now()
        choice=Choice.objects.get(id=choice_id)
        voter=Voter(election=election, user=request.user, vote_hash='hash_vote',cast_at=cast_at)
        voter.save()
        new_vote=Vote(voter=voter, election=election, choice=choice,cast_at=cast_at)
        new_vote.save()
        #print(choice)

    else:
        messages.error(request,'You must select a choice',
                       extra_tags = 'alert alert-danger alert-dismissible fade show')
        return redirect('polls:detail', poll_id = poll_id)
    #return render(request,'polls:index',{'user_can_vote':user_can_vote})
    return redirect("polls:index")
