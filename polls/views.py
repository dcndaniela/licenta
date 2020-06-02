from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from polls.models import Election, Choice
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger



@login_required
def HomeView(request):
    return render(request,'polls/home.html')

@login_required
def IndexView(request):
    if not request.user.is_authenticated:
        #prima {} cu settings.LOGIN_URL; a 2-a {} cu request.path
        settings.configure()
        return redirect('{}?next={}'.format(settings.LOGIN_URL, request.path))
    # cele activate care au start_date inainte de prezentul meu
    polls=Election.objects.filter(isActive=True).filter(start_date__lte = timezone.now()).order_by('start_date')
    if request.user.is_superuser:
        polls = Election.objects.all() #Admin ul vede toate polls

    page = request.GET.get('page', 1)
    paginator = Paginator(polls, 2)
    try:
        polls_paginated = paginator.page(page)
    except PageNotAnInteger:
        polls_paginated = paginator.page(1)
    except EmptyPage:
        polls_paginated = paginator.page(paginator.num_pages)

    context = {'polls': polls_paginated}
    return render(request, 'polls/index.html',context)


@login_required
def DetailView(request,poll_id):
    qs = get_object_or_404(Election, id=poll_id)

    # daca NU este activa sau inca nu a fost publicata, este vizibila doar pentru Admin
    if not qs.isActive or qs.start_date>timezone.now() :
        if not request.user.is_superuser:
            return redirect('polls:index')

    context={'election': qs}
    return render(request, 'polls/detail.html', context)


@login_required
def ResultsView(request,poll_id):
    qs = get_object_or_404(Election, id = poll_id)
    context = {'election': qs}
    return render(request, 'polls/results.html', context)


@login_required
def vote(request, poll_id):
    election = get_object_or_404(Election, pk = poll_id)
    choice_id=request.POST.get('choice')
    if choice_id:
        choice=Choice.objects.get(id=choice_id)
        choice.votes+=1
        choice.save()
    else:
        messages.error(request,'You must select a choice')
        #return redirect('polls:detail', poll_id = poll_id)
        return HttpResponseRedirect(reverse('polls:detail',args=(poll_id,)))
    return redirect('polls:results', poll_id = poll_id)
