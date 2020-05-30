from django.urls import path
from . import views #  din folderul curent


app_name = 'polls'

urlpatterns = [
    # ex: /polls/home
    path('home/', views.HomeView, name='home'), #nu mai adauga nimic la ruta

    # ex: /polls/index
    path('index/', views.IndexView, name='index'),

    # ex: /polls/details/5/
    path('details/<int:poll_id>/', views.DetailView, name='detail'),

    # ex: /polls/5/vote/
    # folosese <> pt a prelua valoarea din ruta; folosesc 'int' pt conversie la int
    #pot sa pun orice nume in loc de 'poll_id', dar trebuie sa fie IDENTIC cu cel din View
    path('details/<int:poll_id>/vote/', views.vote, name='vote'),

    # ex: /polls/5/results/
    path('results/<int:poll_id>/', views.ResultsView, name = 'results'),

]