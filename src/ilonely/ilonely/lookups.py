from ajax_select import register, LookupChannel
from django.contrib.auth.models import User
from django.db.models import Q
from pages.models import Message, Thread
#From ajax select tutorials
@register('userlookup')
class UserLookup(LookupChannel):
    model = User
    def check_auth(self, request):
        if request.user.get_username():
            return True
    def get_query(self, q, request):
        mqs = Message.objects.all().filter(isRequest = False)
        mqs = mqs.filter(Q(thread__userOne__username = request.user.get_username()) | Q(thread__userTwo__username = request.user.get_username()))
        uqs = User.objects.all().filter(Q(username__in = mqs.values_list('thread__userOne__username', flat = True)) | Q(username__in = mqs.values_list('thread__userTwo__username', flat = True)))
        uqs = uqs.exclude(username = request.user.get_username())
        uqs = uqs.filter(username__icontains = q)
        return uqs
    def format_item_display(self,item):
        return u"<span class='tag'>%s</span>" % item.username
