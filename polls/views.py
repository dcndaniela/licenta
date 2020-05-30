from django.http.response import Http404
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.views import generic
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect

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

# For DetailView the question variable is provided automatically – since we’re using a Django model (Question),
# Django is able to determine an appropriate name for the context variable.
#@login_required
def DetailView(request,poll_id):
    #qs = get_object_or_404(Question, id = question_id)
    #user_can_vote = qs.user_can_vote(request.user)
    #results = qs.get_results_dict()
    #context = {'polls': qs, 'user_can_vote': user_can_vote, 'results': results}
    #context={'polls':qs}
    #return render(request, 'polls/detail.html', context)
    qs = get_object_or_404(Question,id=poll_id)
    context={'question': qs}
    return render(request, 'polls/detail.html', context)

#@login_required
# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'

def ResultsView(request,poll_id):
    qs = get_object_or_404(Question, id = poll_id)
    context = {'question': qs}
    return render(request, 'polls/results.html', context)


#@login_required
def vote(request, poll_id):
    question = get_object_or_404(Question, pk=poll_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice']) #returns the ID of the selected choice, as a string
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question, # context= dictionar de perechi key:value ;    key este folosit in html intre {{ }}
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        #pun , dupa question.id pt ca args este un tuplu
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,))) #adica ruta va fi:  '/polls/5/results/' , question.id=5
    # choice_id=request.POST.get('choice')
    # if choice_id:
    #     choice=Choice.objects.get(id=choice_id)
    #     poll = choice.question
    #     choice.votes+=1
    #     choice.save()
    #     return render(request, 'polls/results.html',{'polls':poll})
    # return render(request,'polls/results.html',{'error':True})
