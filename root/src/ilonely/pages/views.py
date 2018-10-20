from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext

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
    return render(
        request,
        'pages/register.html',
        {
            'title':'Registration',
        }
    )

def login(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'pages/login.html',
        {
            'title':'Login',
        }
    )

def forgot_username(request):
    return render(
        request,
        'pages/forgot_username.html',
        {
            'title':'Forgot Username',
        }
    )

def forgot_password(request):
    return render(
        request,
        'pages/forgot_password.html',
        {
            'title':'Forgot Password',
        }
    )