import uuid as uuid
from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from polls.models import Election, Choice, Vote
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from polls.forms import ElectionForm, EditElectionForm, ChoiceForm
import uuid

# !!! Ce trimit in context este vizibil in template(.html) !!!!!










@login_required
def HomeView(request):
    return render(request,'polls/home.html')

@login_required
def IndexView(request):
    searchContent=""#ce contine initial search-ul

    # cele activate care au start_date inainte de prezentul meu
    polls=Election.objects.filter(isActive=True).filter(start_date__lte = timezone.now()).order_by('start_date')
    # if request.user.is_superuser:
    #     polls = Election.objects.all() #Admin ul vede toate polls

    if 'title' in request.GET:#ordonare crescator dupa titlu
        #polls=polls.annotate(Count('vote')).order_by('-vote__count')
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

    context = {'polls': polls_paginated, 'params':params,'searchContent':searchContent}
    return render(request, 'polls/index.html',context)

@login_required
def AddElectionView(request):
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
    if request.user!=poll.owner:
        return redirect ('accounts:login')

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
    if request.user != poll.owner:
        return redirect('accounts:login')

    if request.method == "POST":
        poll.delete()
        messages.success(
            request,
            'Election deleted successfully',
            extra_tags = 'alert alert-success alert-dismissible fade show'
            )
        return redirect('polls:index')
    return render(request, 'polls/delete.html', {'poll': poll})


@login_required
def AddChoiceView(request, poll_id):
    poll=get_object_or_404(Election,id=poll_id)
    if request.user!=poll.owner:
        return redirect ('accounts:login')

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
    if request.user!=poll.owner:
        return redirect ('accounts:login')

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
    if request.user != poll.owner:
        return redirect('accounts:login')

    if request.method == "POST":
        choice.delete()
        messages.success(
        request,
        'Choice deleted successfully',
        extra_tags = 'alert alert-success alert-dismissible fade show'
        )
        return redirect('polls:index')
        #return redirect('polls:edit', choice_id=choice.id)
    return render(request, 'polls/delete_choice.html', {'choice': choice})



@login_required
def DetailView(request,poll_id):
    poll = get_object_or_404(Election, id=poll_id)

    user_can_vote=poll.user_can_vote(request.user)
    # daca NU este activa sau inca nu a fost publicata, este vizibila doar pentru Admin
    if not poll.isActive or poll.start_date>timezone.now() :
        if not request.user.is_superuser:
            return redirect('polls:index')

    context={'election': poll,'user_can_vote':user_can_vote}
    return render(request, 'polls/detail.html', context)


@login_required
def ResultsView(request,poll_id):

    poll = get_object_or_404(Election, id = poll_id)

    if not poll.can_see_results:
        messages.error(request, 'Election is not finished! You can not see the results!')
        return redirect('polls:index')

    user_can_vote = poll.user_can_vote(request.user)
    results=poll.get_results_dict()
    context = {'election': poll, 'results':results }
    return render(request, 'polls/results.html', context)


@login_required
def vote(request, poll_id):
    election = get_object_or_404(Election, pk = poll_id)

    if not election.user_can_vote(request.user):
        messages.error(request, 'You have already voted on this election!')
        return redirect('polls:detail', poll_id = poll_id)

    choice_id=request.POST.get('choice')
    if choice_id:
        #user_uuid=str(uuid.uuid4())
        cast_at=timezone.now()
        choice=Choice.objects.get(id=choice_id)
        new_vote=Vote(user=request.user, election=election, choice=choice,cast_at=cast_at)
        new_vote.save()
        print(choice)
        #choice.votes+=1
        #choice.save()
    else:
        messages.error(request,'You must select a choice')
        #return redirect('polls:detail', poll_id = poll_id)
        return redirect('polls:detail', poll_id = poll_id)
    #return redirect('polls:results', poll_id = poll_id)
    return redirect('polls:index')
