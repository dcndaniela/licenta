from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be published in the future),
        in ordinea descresctaoare publicarii
        """
        return Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5] #Questions care au pub_date<=timezone.now

# For DetailView the question variable is provided automatically – since we’re using a Django model (Question),
# Django is able to determine an appropriate name for the context variable.
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html' #<app_name>/<model_name>_detail.html

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
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
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,))) #adica ruta va fi:  '/polls/5/results/' , question.id=5
