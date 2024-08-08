from django.shortcuts import render, redirect
from .models import User, Event, Submission
from .forms import  SubmissionForm, CustomUserCreationForm, UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import UserCreationForm
from django.http import  HttpResponse
from django.contrib.auth.hashers import make_password
from PIL import Image 
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
import datetime

# Create your views here.
def login_page(request):
    page = "login"
    if request.method  == 'POST':
        user = authenticate(
            email=request.POST['email'],
            password=request.POST['password'])
        if user is not None:
            login(request, user)
            messages.info(request, 'You have successfully logged in')
            return redirect('home')
        else:
            messages.error(request, 'Email or Password is incorrect')
            return redirect ('login')

    context = {'page':page}
    return render(request, 'login_register.html' , context)


def logout_page(request):
    logout(request)
    messages.info(request, 'User is logged out')
    return redirect('login')


def register_page(request):
    page = "register"
    form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            messages.success(request, 'User account was created')
            return redirect('home')
    
     

    context = {'page':page, 'form':form}
    return render(request, 'login_register.html' , context)


def home_page(request):
    limit = request.GET.get('limit')
    if limit == None :
        limit = 20
        limit = int(limit)
    users = User.objects.filter(hackathon_participants=True)
    count = users.count
    page = request.GET.get('page')
    paginator = Paginator(users, 1)
    pages = list(range(1, (paginator.num_pages + 1)))
    try:
        users = paginator.page(page)
    except PageNotAnInteger: 
        page = 1
        users = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages 
        users = paginator.page(page)     
    users = users[0:limit] 
    events = Event.objects.all()
    context = {'users': users, 'events':events, 'count':count, 'paginator':paginator, 'pages':pages}
    return render(request,'home.html', context)

def user_page(request, pk):
    user = User.objects.get(id=pk)

    context = {'user':user}
    return render(request, 'profile.html' ,context)

@login_required(login_url="login")
def account_page(request):
    user = request.user
    context = {'user':user}
    return render(request, 'account.html', context)

@login_required(login_url="login")
def edit_account(request):
    form = UserForm(instance=request.user)

    if request.method == 'POST':
      form = UserForm(request.POST, request.FILES, instance=request.user)
    if form.is_valid():
            form.save()
            return redirect ('account')
    context = {'form':form}
    return render(request,'user_edit.html', context)

@login_required(login_url="login")
def change_password(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            newPassword = make_password(password1)
            request.user.password = newPassword
            request.user.save()
            return redirect('account')
        messages.info(request, 'You have successfully reset your password!')
    context = {}
    return render(request, 'change_password.html', context)

import time
from datetime import datetime, timedelta 
def event_page(request, pk):
    event = Event.objects.get(id=pk)

    present = datetime.now().timestamp()
    deadline = event.registration_deadline.timestamp()
    present_deadline = (present > deadline)
    register = False
    submitted = False

    if request.user.is_authenticated:
        register = request.user.event.filter(id=event.id).exists()
        submitted = Submission.objects.filter(participant=request.user, event=(event)).exists()

    context = {'event':event, 'register':register, 'submitted':submitted, 'present_deadline':present_deadline}
    return render(request, 'event.html', context)


@login_required(login_url="login")
def registration_confirmation(request, pk):
    event = Event.objects.get(id=pk)

    if request.method == 'POST':
        event.participants.add(request.user)
        return redirect('event', pk=event.id)

    context = {'event':event} 
    return render(request, 'event_confirmation.html', context)


#@login_required(login_url="login")
def project_submission(request, pk):
    event = Event.objects.get(id=pk)

    form = SubmissionForm()

    if request.method == 'POST':
        form =  SubmissionForm(request.POST)
        if form.is_valid():
           submission = form.save(commit=False)
           submission.participants = request.user
           submission.event = event
           submission.save()
       
          
        return redirect('account')
        
    context = {'event':event, 'form':form}
    return render(request, 'submit_form.html', context)


#add owner authentication
def update_submission(request, pk):
    submission = Submission.objects.get(id=pk)

    if request.user != submission.participant:
     return HttpResponse('You are not allow here')

    event = submission.event
    form = SubmissionForm(instance=submission)

    if request.method == 'POST':
        form =  SubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.participant = request.user
            submission.event = event
        return redirect('account')
    
    context = {'event':event, 'form':form}
    return render(request, 'submit_form.html', context) 

