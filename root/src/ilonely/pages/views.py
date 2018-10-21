from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .forms import CustomUserCreationForm

# Create your views here.

def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'pages/home.html',
        {
            'title':'Home',
        }
    )

def register(request):
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('success')
        else:
            messages.error(request, 'Account not created successfully.')
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        'pages/register.html',
        {
            'title':'Registration',
            'form':form
        }
    )

def login_view(request):
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Log in the user
            user = form.get_user()
            login(request, user)
            # Take user to their home page
            return redirect('user_home')
        else:
            # Print error message
            print("Failure")
    else:
        form = AuthenticationForm()
    return render(
        request,
        'pages/login.html',
        {
            'title':'Login',
            'form':form
        }
    )

def forgot_username_view(request):
    return render(
        request,
        'pages/forgot_username.html',
        {
            'title':'Forgot Username',
        }
    )

def forgot_password_view(request):
    return render(
        request,
        'pages/forgot_password.html',
        {
            'title':'Forgot Password',
        }
    )

def success(request):
    return render(
        request,
        'pages/success.html',
        {
            'title':'Sucessful Login'
        }
    )

def user_home_view(request):
    return render(
        request,
        'pages/user_home.html',
        {
            'title':'User Home Page'
        }
    )