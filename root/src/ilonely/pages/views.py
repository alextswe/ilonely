from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .forms import CustomUserCreationForm, ProfileForm
from pages.models import Profile, Follow, Block
import random,string

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
        pform = ProfileForm(data=request.POST)

        # Automatically signs the user in
        if form.is_valid() and pform.is_valid():
            user = form.save()
            profile = user.profile
            profile.age = pform.cleaned_data.get('age')
            profile.save()
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
        pform = ProfileForm()

    return render(
        request,
        'pages/register.html',
        {
            'title':'Registration',
            'form':form,
            'pform':pform,
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
            user.email_user(
                subject='iLonely: Account Username',
                message = 'Did you forget your username? Don\'t worry, we didn\'t. Your username is: %s!' % user.get_username()
            )
        messages.success(request, "We sent an email to your account.");      
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
                password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(7))
                user.set_password(password)
                user.save()
                user.email_user(
                subject='iLonely: Reset Account Password',
                message = 'Hi {0}! Your password has been reset to: {1} \nCopy and paste this into the login page to finish resetting your password'.format(user.get_username(),password) 
            )
        messages.success(request, "An email has been sent to your account with further instructions.")  
       
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
    return render(request,'pages/user_home.html', {'title':'User Home Page'})

# Prevents anyone from accessing this page unless they are logged in to their account
@login_required(login_url="home")
def notifications_view(request):
    me = User.objects.get(pk=request.user.id)
    # Message Notifications:
    # ---Search for all pending message requests 
    # ---   and load profiles associated with them

    # Follow Notifications:
    # ---Search for all pending follow requests 
    # ---   and load profiles associated with them
    return render(request, 'pages/notifications.html', 
                    {   'title':'Notifications',
                        
                     }
                  )

@login_required(login_url="home")
def view_following(request):
    if request.method == 'POST':
        viewUser = request.POST['viewUser']
        return redirect(public_profile, userid = viewUser)
    else:
        me = User.objects.get(pk=request.user.id)
        #need to exclude blocked users
        if Follow.objects.filter(userFollowing=me):
            followSet = User.objects.filter(pk__in = Follow.objects.filter(userFollowing = me).values_list('user'))
            profilesIFollow = list(Profile.objects.filter(user__in = followSet))
        else:
            profilesIFollow = None
        return render(request, 'pages/view_following.html', 
                    { 'title':'Following', 'following' : profilesIFollow,} )

@login_required(login_url="home")
def view_nearby(request):
    if request.method == 'POST':
        viewUser = request.POST['viewUser']
        return redirect(public_profile, userid = viewUser)
    else:
        me = User.objects.get(pk=request.user.id)
        myProfile = Profile.objects.filter(user = me).first()
        #need to exclude blocked users
        peopleNearMe = Profile.objects.filter(location = myProfile.location).exclude(user = me).all() #need to convert locations to lowercase
        return render(request, 'pages/view_nearby.html', {'title':'Nearby', 'people' : peopleNearMe,})

@login_required(login_url="home")
def public_profile(request, userid):
    if request.method == 'POST':
        me = User.objects.get(pk = request.user.id)
        if request.POST.get('followUser'):
            followUser = User.objects.get(pk = request.POST['followUser'])           
            try:
                f = Follow.objects.get(userFollowing=me, user=followUser)
                f.delete()
            except Follow.DoesNotExist:
                f = Follow(userFollowing=me, user=followUser, isRequest=True)
                f.save()
        elif request.POST.get('messageUser'):
            return redirect('Not implemented')
        elif request.POST.get('blockUser'):
            blockUser = User.objects.get(pk = request.POST['blockUser'])
            try:
                b = Block.objects.get(userBlocking=me, user=blockUser)
                b.delete()
            except Block.DoesNotExist:
                b = Block(userBlocking=me, user=blockUser)
                b.save()     
    profile = Profile.objects.filter(user = userid).first()
    following = Follow.objects.filter(userFollowing=User.objects.get(pk = request.user.id), user=User.objects.get(pk = userid)).exists()
    blocking = Block.objects.filter(userBlocking=User.objects.get(pk = request.user.id), user=User.objects.get(pk = userid)).exists()
    return render(request, 'pages/public_profile.html', 
                {'title': (profile.user.first_name + ' ' + profile.user.last_name), 
                'profile' : profile,'following' : following, 'blocking' : blocking})

@login_required(login_url="home")
def my_profile(request):
    userid = request.user
    profile = Profile.objects.filter(user = userid).first()
    if request.method == 'POST':
        if request.POST.get('editFields'):
            newfname = request.POST.get("fnamespace")
            newlname = request.POST.get("lnamespace")
            newage = request.POST.get("agespace")
            newbio = request.POST.get("biospace")
            #Handle age and bio errors here
            if newage.isdigit() :
                profile.age = newage
            profile.bio = newbio
            userid.first_name = newfname
            userid.last_name = newlname
        elif request.POST.get('uploadButton'):
            profile.photo = request.FILES['myfile'] 
        userid.save()
        profile.save()
        return render(request, 'pages/my_profile.html', 
                        {'title': (profile.user.first_name + ' Profile Page'),
                        'profile' : profile,})
    else:
        return render(request, 'pages/my_profile.html',
                    {'title': (profile.user.first_name + ' Profile Page'),
                    'profile' : profile,})

def dataviewer(request):
    users = User.objects.all()
    profiles = Profile.objects.all()
    follows = Follow.objects.all()
    blocks = Block.objects.all()
    return render(request, 'pages/dataviewer.html', 
                  {'title': 'View the data', 
                   'users': users, 
                   'profiles' : profiles, 
                   'follows' : follows, 
                   'blocks' : blocks,})
