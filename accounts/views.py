from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from . forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.


def LoginView(request):
    if request.method=="POST":
       # print(request.POST)
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user is not None:
            #print(request.GET)
            login(request, user)
            #return HttpResponseRedirect(reverse('polls:home')) #home= name dat in urls din polls
            return redirect('polls:home')  # home= name dat in urls din polls
        else:
            messages.error(request, 'Bad username or password')
    return render(request, 'accounts/login.html',{}) # {}= dictionary

@login_required     #folosesc acest decorator in loc sa implementez pentru fiecare
def LogoutView(request):
 #  return render(request, 'accounts/logout.html',{})
    logout(request)
    #return HttpResponseRedirect(reverse('polls:home'))
    return redirect('accounts:login')


def RegisterView(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():# is_valid apeleaza automat clean()
            #print(form.cleaned_data) #cleaned_data este un dictionary(key-value); merge doar daca am is_valid() inainte
            usern= form.cleaned_data['username']
            passw=form.cleaned_data['password1'] #cleaned_data este un dictionary
            emailn=form.cleaned_data['email']
            user=User.objects.create_user(usern, email=emailn, password=passw) #creez User
            messages.success(request, 'Thank you for registering {}'.format(user.username))
            #return HttpResponseRedirect(reverse('accounts:login'))
            return redirect('accounts:login')
            #print('User nou creat!')
    else:
        form=RegisterForm()
    return render(request, 'accounts/register.html',{'form': form} )






