from django.http.response import Http404
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.views import generic
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from polls.models import Question, Choice
from django.contrib.auth.decorators import login_required


def HomeView(request):
    return render(request,'polls/home.html')

@login_required
def IndexView(request):
    if not request.user.is_authenticated:
        #prima {} cu settings.LOGIN_URL; a 2-a {} cu request.path
        settings.configure()
        return redirect('{}?next={}'.format(settings.LOGIN_URL, request.path))
    polls=Question.objects.all()
    context={'polls':polls}
    return render(request, 'polls/index.html',context)

# Return the last five published questions (not including those set to be published in the future),
# in ordinea descresctaoare publicarii
     #   return Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5] #Questions care au pub_date<=timezone.now

@login_required
def DetailView(request,poll_id):
    qs = get_object_or_404(Question,id=poll_id)
    context={'question': qs}
    return render(request, 'polls/detail.html', context)

@login_required

def ResultsView(request,poll_id):
    qs = get_object_or_404(Question, id = poll_id)
    context = {'question': qs}
    return render(request, 'polls/results.html', context)


@login_required
def vote(request, poll_id):
    question = get_object_or_404(Question, pk = poll_id)
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
