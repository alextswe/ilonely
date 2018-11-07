"""
Definition of urls for ilonely.
"""

from datetime import datetime
from django.conf.urls import include, url
from django.urls import path
import django.contrib.auth.views
import django.contrib.auth.urls
import pages.views
# enables admin site
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = [
    url(r'^$', pages.views.home, name='home'),
    url(r'^register$', pages.views.register, name='register'),
    url(r'^login$', pages.views.login_view, name='login'),
    url(r'^logout$', pages.views.logout_view, name='logout'),
    url(r'^forgot_username$', pages.views.forgot_username_view, name='forgot_username'),
    url(r'^forgot_password$', pages.views.forgot_password_view, name='forgot_password'),
    url('^', django.contrib.auth.urls),
    #url(r'^password_reset/$', pages.views.password_reset, name='password_reset'),
    #url(r'^password_reset/done/$', pages.views.password_reset_done, name='password_reset_done'),
    #url(r'^password_reset_confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',pages.views.password_reset_confirm, name='password_reset_confirm'),
    #url(r'^reset/done/$', pages.views.password_reset_complete, name='password_reset_complete'),
    url(r'^success$', pages.views.success, name='success'),
    url(r'^user_home$', pages.views.user_home_view, name='user_home'),
    url(r'^notifications$', pages.views.notifications_view, name='notifications'),
    url(r'^view_following$', pages.views.view_following, name='view_following'),
    url(r'^view_nearby$', pages.views.view_nearby, name='view_nearby'),
    url(r'^public_profile/(?P<userid>\d+)/$', pages.views.public_profile, name='public_profile'),
    url(r'^my_profile/$', pages.views.my_profile, name='my_profile'),
    url(r'^feed$', pages.views.feed, name='feed'),
    url(r'^admin/', admin.site.urls), # admin site url
    url(r'^messages/', include('postman.urls', namespace='postman')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
