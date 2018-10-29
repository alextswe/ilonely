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
from .forms import CustomUserCreationForm
from pages.models import Profile, Follow, Block, Thread, Message
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

        # Automatically signs the user in
        if form.is_valid():
            user = form.save()
            user.profile.age = form.cleaned_data.get('age')
            print(form.cleaned_data.get('age'))
            user.profile.save()
            user.save()
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
            'form':form,
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
    if request.method == 'POST':
        viewUser = request.POST['viewUser']
        return redirect(public_profile, userid = viewUser)
    else:
        me = User.objects.get(pk=request.user.id)
        # Message Notifications:
        # --- Message requests "I" have sent
        try:
            myRequests = Message.objects.filter(author=me, isRequest=True)
            threadSet = Thread.objects.filter(pk__in = myRequests.values_list('thread')) 
            requestSet = User.objects.filter(pk__in = threadSet.values_list('userTwo'))
            myMsgRequestProfiles = list(Profile.objects.filter(user__in = requestSet))
        except Message.DoesNotExist:
            myMsgRequestProfiles = None

        # --- Message requests users have sent "me"
        try:
            threadSet = Thread.objects.filter(userTwo=me)
            userRequests = Message.objects.filter(thread__in = threadSet, isRequest=True)
            requestSet = User.objects.filter(pk__in = userRequests.values_list('author'))
            userRequestProfiles = list(Profile.objects.filter(user__in = requestSet))
        except ObjectDoesNotExist:
            userRequestProfiles = None

        # FIXME: Follow Notifications:
        # ---Search for all pending follow requests 
        # ---   and load profiles associated with them
    return render(request, 'pages/notifications.html', 
                    {   'title':'Notifications',
                        'my_message_requests': myMsgRequestProfiles,
                        'user_message_requests': userRequestProfiles,
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
            # Find the user we want to message in the database
            messageUser = User.objects.get(pk = request.POST['messageUser'])
            try:
                # Check if there is a thread indicating the users are already messaging
                m1 = Thread.objects.get(userOne=me, userTwo=messageUser)
                m1.delete()
            except Thread.DoesNotExist:
                try:
                    m2 = Thread.objects.get(userOne=messageUser, userTwo=me)
                    m2.delete()
                except Thread.DoesNotExist:
                    # A thread does not exist, so create a new thread between the users
                    m2 = Thread(userOne=me, userTwo=messageUser)
                    m2.save()
                    # Sends message request to a user
                    newMessage = Message(thread=m2, author=me, isRequest=True)
                    newMessage.save()
                
            #return redirect('Not implemented')
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
    try:
        myRequests = Message.objects.filter(author=User.objects.get(pk = request.user.id), isRequest=True)
        threadSet = Thread.objects.filter(pk__in = myRequests.values_list('thread')) 
        requestSet = User.objects.filter(pk__in = threadSet.values_list('userTwo'))
        messaging = None
        for user in requestSet:
            if user == User.objects.get(pk = userid):
                messaging = True
    except Message.DoesNotExist:
        messaging = None
    return render(request, 'pages/public_profile.html', 
                {'title': (profile.user.first_name + ' ' + profile.user.last_name), 
                'profile' : profile,
                'following' : following,
                'blocking' : blocking,
                'messaging' : messaging,
                }
                  )

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
