import axes
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from . forms import RegisterForm
from accounts.models import CustomUser as User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
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
            messages.error(request, 'Bad username or password',
                           extra_tags = 'alert alert-danger alert-dismissible fade show')
    return render(request, 'accounts/login.html',{}) # {}= dictionary

@login_required     #folosesc acest decorator in loc sa implementez pentru fiecare
def LogoutView(request):
 #  return render(request, 'accounts/logout.html',{})
    logout(request)
    return redirect('accounts:login')


def RegisterView(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():# is_valid apeleaza automat clean()
            #print(form.cleaned_data) #cleaned_data este un dictionary(key-value); merge doar daca am is_valid() inainte
            cnpu= form.cleaned_data['cnp']
            passw=form.cleaned_data['password1'] #cleaned_data este un dictionary
            phoneu=form.cleaned_data['phone']
            user=User.objects.create_user(cnp=cnpu, phone=phoneu, password=passw) #creez User
            # messages.success(request, 'Thank you for registering, {} !'.format(user.username),
            #                  extra_tags = 'alert alert-success alert-dismissible fade show')
            messages.success(request, 'Thank you for registering!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('accounts:login')
    else:
        form=RegisterForm()
    return render(request, 'accounts/register.html',{'form': form} )


def FailedLogInView(request):
    return render(request, 'accounts/failed_login.html',{})


@login_required
def ChangePasswordView(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user=form.save()
            update_session_auth_hash(request, user)#User-ul ramane logat dupa ce isi schimba parola
            messages.success(request, 'Password successfully changed!',
                             extra_tags = 'alert alert-success alert-dismissible fade show')
            return redirect('polls:home')
        else:
            messages.error(request, 'Please correct the error below.',
                           extra_tags = 'alert alert-danger alert-dismissible fade show')
            return redirect('accounts:change_password')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})



