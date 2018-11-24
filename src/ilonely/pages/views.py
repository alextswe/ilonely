from .forms import CustomUserCreationForm, CustomForgotUsernameForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, QueryDict
from django.shortcuts import render, redirect, resolve_url
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from geopy.geocoders import Nominatim
from instagram.client import InstagramAPI
from pages.geo import getNearby
from pages.models import Profile, Follow, Block, Thread, Message, Post
import json
import random,string
import requests
# Create your views here.

INSTAGRAM_CLIENT_ID = '9788a776a2e44e7a842fc85132f528dc' # Keep Secret
INSTAGRAM_CLIENT_SECRET = '1a18bbccc88b4d0ca151edc06d39ed37' # Really Keep Secret
INSTAGRAM_REDIRECT_URI = 'http://localhost:8000/Instalink/'
instagram_auth_url = 'https://api.instagram.com/oauth/authorize/?client_id=' + INSTAGRAM_CLIENT_ID + '&redirect_uri=' + INSTAGRAM_REDIRECT_URI + '&response_type=code'


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
            login(request, user, 'django.contrib.auth.backends.ModelBackend')
            user.email_user(
                subject='Welcome to iLonely!',
                message = 'Hi %s! We hope you\'ll enjoy iLonely!' % user.get_username()
            )
            return redirect('success')
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
            login(request, user, 'django.contrib.auth.backends.ModelBackend')
            # Take user to their home page
            return redirect('user_home') 
    else:
        form = AuthenticationForm()
    return render(
        request,
        'registration/login.html',
        {
            'title':'Login',
            'form':form,
        }
    )

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return

def forgot_username_view(request):
    assert isinstance(request, HttpRequest)
    confirm = False
    if request.method == 'POST':
        form = CustomForgotUsernameForm(data=request.POST)
        if form.is_valid:
            confirm = True
            try:
                user = User.objects.filter(email=form['email']).first()
            except User.DoesNotExist:
                user = None
            if user is not None:
                user.email_user(
                    subject='iLonely: Account Username',
                    message = 'Did you forget your username? Don\'t worry, we didn\'t. Your username is: %s' % user.get_username()
                )
    else:
        form = CustomForgotUsernameForm()
    return render(
        request,
        'registration/forgot_username.html',
        {
            'title':'Forgot Username',
            'form': form,
            'confirm': confirm,
            'confirmation_message': 'We sent an email with your username to your account'
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
    me = User.objects.get(pk=request.user.id)
    myProfile = Profile.objects.get(user = me)
    if request.method == 'POST':
        if request.POST.get('viewUser'):
            return redirect(public_profile, userid = request.POST['viewUser'])
        elif request.POST.get('deletePost'):
            postid = request.POST['deletePost']
            p = Post.objects.get(pk = postid)
            p.delete()
        else:
            myPost = request.POST['postContent']
            p = Post(profile=myProfile, postContent=myPost)
            p.save()
    #posts of people I follow
    followSet = User.objects.filter(pk__in = Follow.objects.filter(userFollowing = me).values_list('user'))
    profilesIFollow = Profile.objects.filter(user__in = followSet)
    followingPosts = list(Post.objects.filter(profile__in = profilesIFollow).order_by('-datePosted'))
    #posts of people nearby
    profilesNearMe = getNearby(me, 10)
    profilesIBlock = User.objects.filter(pk__in = Block.objects.filter(userBlocking = me).values_list('user'))
    blockedUsers = list(Profile.objects.filter(user__in = profilesIBlock))
    nearby = list(Post.objects.filter(profile__in = profilesNearMe).order_by('-datePosted'))
    nearbyPosts = []
    for i in nearby:
        if i in blockedUsers:
            continue
        else:
            nearbyPosts.append(i)        
        
    #myPosts
    personalPosts = list(Post.objects.filter(profile = myProfile).order_by('-datePosted'))
    return render(request, 'pages/user_home.html', {'title' : 'User Home', 
                                               'followingPosts' : followingPosts, 
                                               'nearbyPosts' : nearbyPosts,
                                               'personalPosts' : personalPosts,
                                               'instagram_auth':instagram_auth_url,})

@login_required(login_url="home")
def set_location(request): 
    if request.method == 'POST':
        me = User.objects.get(pk=request.user.id)
        profile = Profile.objects.get(user = me)
        profile.latitude = request.POST.get('latitude')
        profile.longitude = request.POST.get('longitude')
        geolocator = Nominatim(user_agent="ilonely")
        location = geolocator.reverse("%s, %s" % (profile.latitude, profile.longitude))
        state = location.raw['address']['state']
        try:
            city = (location.raw['address']['city'])
        except:
            city = (location.raw['address']['hamlet'])
        profile.location = ("%s, %s") % (city, state)
        profile.save()
        return HttpResponse(status=204)
    else:
        return HttpResponseBadRequest(request)

# Prevents anyone from accessing this page unless they are logged in to their account
@login_required(login_url="home")
def notifications_view(request):
    def get_my_msg_requests(me):
        # --- Message requests "I" have sent
        try:
            myRequests = Message.objects.filter(author=me, isRequest=True)
            threadSet = Thread.objects.filter(pk__in = myRequests.values_list('thread')) 
            requestSet = User.objects.filter(pk__in = threadSet.values_list('userTwo'))
            myMsgRequestProfiles = list(Profile.objects.filter(user__in = requestSet))
        except ObjectDoesNotExist:
            myMsgRequestProfiles = None
        return myMsgRequestProfiles
    def get_user_msg_requests(me):
        # --- Message requests users have sent "me"
        try:
            threadSet = Thread.objects.filter(userTwo=me)
            userRequests = Message.objects.filter(thread__in = threadSet, isRequest=True)
            requestSet = User.objects.filter(pk__in = userRequests.values_list('author'))
            userRequestProfiles = list(Profile.objects.filter(user__in = requestSet))
        except ObjectDoesNotExist:
            userRequestProfiles = None
        return userRequestProfiles
    def update_user_msg_requests(me, user, isAccepted):
        try:
            threadSet = Thread.objects.get(userOne=user, userTwo=me)
            userRequest = Message.objects.get(thread = threadSet, isRequest=True)
            if isAccepted:
                userRequest.isRequest = False
                userRequest.save()
            else:
                threadSet.delete()
                userRequest.delete()
        except ObjectDoesNotExist:
            # Do nothing
            threadSet = None
        return
    if request.method == 'POST':
        if request.POST.get('viewUser'):
            viewUser = request.POST['viewUser']
            return redirect(public_profile, userid = viewUser)
        elif request.POST.get('acceptMsg'):
            user = request.POST['acceptMsg']
            update_user_msg_requests(User.objects.get(pk=request.user.id), User.objects.get(pk = user), True)
        elif request.POST.get('declineMsg'):
            user = request.POST['declineMsg']
            update_user_msg_requests(User.objects.get(pk=request.user.id), User.objects.get(pk = user), False)
        
        return redirect('notifications')
    else:
        me = User.objects.get(pk=request.user.id)
        # Message Notifications:
        
        myMsgRequestProfiles = get_my_msg_requests(me)
        userRequestProfiles = get_user_msg_requests(me)

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
        #blocked users are removed from the follow list
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
        if request.POST.get('viewUser'):
            viewUser = request.POST['viewUser']
            return redirect(public_profile, userid = viewUser)
    elif request.method == 'GET':
        distList=[]
        peopleNearMe=[]
        miles = 10
        age = None
        me = User.objects.get(pk=request.user.id)
        myProfile = Profile.objects.get(user = me)

        if request.GET.get('ageFilter'):
            age = int(request.GET['ageFilter'])

        if request.GET.get('milesFilter'):
            miles = int(request.GET['milesFilter'])

        peopleNear = getNearby(me, miles, distList, age)       
        peopleNearMe=blockUsers(peopleNear, me)
        return render(request, 
                        'pages/view_nearby.html', 
                        {'title':'Nearby', 
                        'people': zip(peopleNearMe, distList),
                        'profile': myProfile,
                        'radius': miles})
    else:
        distList=[]
        peopleNearMe=[]
        me = User.objects.get(pk=request.user.id)
        myProfile = Profile.objects.get(user = me)
        peopleNear = getNearby(me, 10, distList)
        peopleNearMe=blockUsers(peopleNear, me)
        return render(request, 
                        'pages/view_nearby.html', 
                        {'title':'Nearby', 
                        'people': zip(peopleNearMe, distList),
                        'profile': myProfile,
                        'zoom': 10})

@login_required(login_url="home")
def public_profile(request, userid):
    def is_msg_request(me, user):
        try:
            threadSet = Thread.objects.get(userOne=me, userTwo=user) 
            myRequests = Message.objects.get(author=me, thread=threadSet, isRequest=True)
            return True            
        except ObjectDoesNotExist:
            return False
    def is_pending_approval(me, user):
        try:
            threadSet = Thread.objects.get(userOne=user, userTwo=me) 
            myRequests = Message.objects.get(thread=threadSet, isRequest=True)
            return True            
        except ObjectDoesNotExist:
            return False
    def is_messagable(me, user):
        try:
            threadSet = Thread.objects.get(userOne=me, userTwo=user) 
            myRequests = Message.objects.get(author=me, thread=threadSet, isRequest=False)
            return True            
        except ObjectDoesNotExist:
            try:
                threadSet = Thread.objects.get(userOne=user, userTwo=me) 
                myRequests = Message.objects.get(thread=threadSet, isRequest=False)
                return True            
            except ObjectDoesNotExist:
                return False
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
                # If userOne = me, I sent a message request
                m = Thread.objects.get(userOne=me, userTwo=messageUser)
                try:
                    userRequest = Message.objects.get(thread = m, isRequest=True)
                    # If the message has not been confirmed, I can remove the request
                    m.delete()
                except Message.DoesNotExist:
                    # If the message has been confirmed, go to message page so I can chat
                    return redirect('messaging')
            except Thread.DoesNotExist:
                # If userTwo = me, I receieved a message request
                try:
                    m = Thread.objects.get(userOne=messageUser, userTwo=me)
                    try:
                        userRequest = Message.objects.get(thread = m, isRequest=True)
                        # If the message has not been confirmed, go to notifications page to accept/decline
                        return redirect('notifications')
                    except Message.DoesNotExist:
                        # If the message has been confirmed, go to message page so I can chat
                        return redirect('messaging')
                except Thread.DoesNotExist:
                    # A thread does not exist between the users, so create a new thread
                    m = Thread(userOne=me, userTwo=messageUser)
                    m.save()
                    # Sends message request to a user
                    newMessage = Message(author=me, thread=m, isRequest=True)
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
            
            try:
                f = Follow.objects.get(userFollowing=me, user=blockUser)
                f.delete()
            except Follow.DoesNotExist:
                f = Follow(userFollowing=me, user=blockUser)

    profile = Profile.objects.filter(user = userid).first()
    following = Follow.objects.filter(userFollowing=User.objects.get(pk = request.user.id), user=User.objects.get(pk = userid)).exists()
    blocking = Block.objects.filter(userBlocking=User.objects.get(pk = request.user.id), user=User.objects.get(pk = userid)).exists()

    message_request = is_msg_request(User.objects.get(pk = request.user.id), User.objects.get(pk = userid))
    pending_approval = is_pending_approval(User.objects.get(pk = request.user.id), User.objects.get(pk = userid))
    messagable = is_messagable(User.objects.get(pk = request.user.id), User.objects.get(pk = userid))
    return render(request, 'pages/public_profile.html', 
                {'title': (profile.user.first_name + ' ' + profile.user.last_name), 
                'profile' : profile,
                'following' : following,
                'blocking' : blocking,
                'message_request' : message_request,
                'pending_approval' : pending_approval,
                'messagable': messagable,
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
                        'profile' : profile,
                        }
                      )
    else:
        return render(request, 'pages/my_profile.html',
                        {'title': (profile.user.first_name + ' Profile Page'),
                        'profile' : profile,
                        }
                      )

@login_required(login_url="home")
def feed(request):
    me = User.objects.get(pk=request.user.id)
    myProfile = Profile.objects.get(user = me)
    if request.method == 'POST':
        if request.POST.get('viewUser'):
            return redirect(public_profile, userid = request.POST['viewUser'])
        elif request.POST.get('deletePost'):
            postid = request.POST['deletePost']
            p = Post.objects.get(pk = postid)
            p.delete()
        else:
            myPost = request.POST['postContent']
            p = Post(profile=myProfile, postContent=myPost)
            p.save()
    #posts of people I follow
    followSet = User.objects.filter(pk__in = Follow.objects.filter(userFollowing = me).values_list('user'))
    profilesIFollow = Profile.objects.filter(user__in = followSet)
    followingPosts = list(Post.objects.filter(profile__in = profilesIFollow).order_by('-datePosted'))
    #posts of people nearby
    profilesNearMe = getNearby(me, 10)
    nearbyPosts = list(Post.objects.filter(profile__in = profilesNearMe).order_by('-datePosted'))
    #profilesIBlock = list(Profile.objects.filter(user__in = blockSet))
    #myPosts
    personalPosts = list(Post.objects.filter(profile = myProfile).order_by('-datePosted'))
    return render(request, 'pages/feed.html', {'title' : 'feed', 
                                               'followingPosts' : followingPosts, 
                                               'nearbyPosts' : nearbyPosts,
                                               'personalPosts' : personalPosts})

def blockUsers(peopleNear, me):
    profilesIBlock = User.objects.filter(pk__in = Block.objects.filter(userBlocking = me).values_list('user'))
    blockedUsers = list(Profile.objects.filter(user__in = profilesIBlock))
    peopleNearMe = []

    for i in peopleNear:
        if i in blockedUsers:
            continue
        else:
            peopleNearMe.append(i)  

    return peopleNearMe

@login_required(login_url="home")
def linkInstagram(request):
    # Fixme: Hide code from url and silently fail when someone enters a code in url
    def get_access_code(code):
        if code != None:
            url = 'https://api.instagram.com/oauth/access_token'
            data = {
                'client_id': INSTAGRAM_CLIENT_ID,
                'client_secret': INSTAGRAM_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': INSTAGRAM_REDIRECT_URI,
                'code': code
            }
            r = requests.post(url, data=data)
            parsed_json = json.loads(r.text)
            access_token = parsed_json['access_token']
            return access_token
        else:
            return None
    def get_media(code):
        access_token = get_access_code(code)
        media_urls = []
        if access_token != None:
            url = 'https://api.instagram.com/v1/users/self/media/recent/?access_token=' + access_token
            r = requests.get(url)
            parsed_json = json.loads(r.text)
            for row in parsed_json['data']:
                media_urls.append(row.get('images').get('low_resolution').get('url'))
            return media_urls
        else:
            return None

    code = request.GET.get('code',None)
    media_urls = get_media(code)
    if media_urls != None:
        # Fixme: Update html file to feed.html
        return render(request, 'instagram/upload_pictures.html',
                  {
                      'media_urls' : media_urls,
                  }
                 )
    else:
        # Fail silently
        return redirect('home')
   
@login_required(login_url="home")
def uploadInstapics(request):
    return render(request, 'instagram/upload_pictures.html',
                  {
                  }
                 )