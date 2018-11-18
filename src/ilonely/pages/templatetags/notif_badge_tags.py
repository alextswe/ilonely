from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from pages.models import Profile, Follow, Block, Thread, Message, Post
from django import template

register = template.Library()

@register.inclusion_tag('pages/notification_badge.html')
def show_new_notifications(uid):
    try:
        me = User.objects.get(pk=uid)
        threadSet = Thread.objects.filter(userTwo=me)
        userRequests = Message.objects.filter(thread__in = threadSet, isRequest=True)
        requestSet = User.objects.filter(pk__in = userRequests.values_list('author'))
        userRequestProfiles = list(Profile.objects.filter(user__in = requestSet))
    except ObjectDoesNotExist:
        userRequestProfiles = None
    return {'new_notifications': len(userRequestProfiles)}