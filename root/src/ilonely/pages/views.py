from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .forms import CustomUserCreationForm
from pages.models import Profile, Follow, Block

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

        # Automatically signs the user in
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            user.email_user(
                subject='Welcome to iLonely!',
                message = 'Hi %s! We hope you\'ll enjoy iLonely!' % user.get_username()
            )
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
            messages.error(request, 'Incorrect username or password')
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

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return

def forgot_username_view(request):
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        email = request.POST.get("email", None)
        try:
            user = User.objects.filter(email=email).first()
        except User.DoesNotExist:
            user = None
        if user is not None:
            print(user.get_username())
                
    return render(
        request,
        'pages/forgot_username.html',
        {
            'title':'Forgot Username',
        }
    )

def forgot_password_view(request):
    assert isinstance(request, HttpRequest)
    if request.method == 'POST':
        username = request.POST.get("username", None)
        try:
            user = User.objects.filter(username=username).first()
        except User.DoesNotExist:
            user = None
        if user is not None:
            if user.get_username() == username:
                password = "password"
                user.set_password(password)
                user.save()
                
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

# Prevents anyone from accessing this page unless they are logged in to their account
@login_required(login_url="home")
def user_home_view(request):
    return render(
        request,
        'pages/user_home.html',
        {
            'title':'User Home Page'
        }
)

def view_following(request):
    if request.method == 'POST':
        viewUser = request.POST['viewUser']
        return redirect(public_profile, userid = viewUser)
    else:
        me = request.user.id
        followset = Follow.objects.filter(userFollowing=me)
        usersIFollow = Profile.objects.filter(user = followset.user)
        return render(request, 'pages/view_following.html', 
                    { 'title':'Following', 
                    'following' : usersIFollow,} )

def view_nearby(request):
    if request.method == 'POST':
        viewUser = request.POST['viewUser']
        return redirect(public_profile, userid = viewUser)
    else:
        me = request.user.id
        myProfile = Profile.objects.filter(user = me)
        peopleNearMe = Profile.objects.filter(location = myProfile.location) #need to convert locations to lowercase
        return render(request, 'pages/view_nearby.html', {'title':'Nearby', 'people' : peopleNearMe,})

def public_profile(request, userid):
    if request.method == 'POST':
        if request.POST.get('followUser'):
            followUser = request.POST['followUser']
            f = Follow.objects.filter(userFollowing=request.user.id, user=followUser)
            if f is None: 
                f = Follow(userFollowing=request.user.id, user=followUser, isRequest=True)
                f.save()
            else:
                f.delete() #already following so unfollow
        elif request.POST.get('messageUser'):
            return redirect('Not implemented')
        elif request.POST.get('blockUser'):
            blockUser = request.POST['blockUser']
            b = Block.objects.filter(userBlocking=request.user.id, user=blockUser)
            if b is None:
                b = Block(userBlocking=request.user.id, user_home_view=blockUser)
                b.save()
            else: #already blocking user so unblock
                b.delete()       
    else:
        profile = Profile.objects.filter(user = userid)
        return render(request, 'pages/public_profile.html', 
                    {'title': (profile.first_name + ' ' + profile.last_name), 
                    'profile' : profile,})