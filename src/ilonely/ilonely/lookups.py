from ajax_select import register, LookupChannel
from django.contrib.auth.models import User

#From ajax select tutorials
@register('userlookup')
class UserLookup(LookupChannel):
    model = User
    def get_query(self, q, request):
        return self.model.objects.filter(username_icontains = q)
    def format_item_display(self,item):
        return u"<span class='tag'>%s</span>" % item.name
