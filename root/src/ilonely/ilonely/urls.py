"""
Definition of urls for ilonely.
"""

from datetime import datetime
from django.conf.urls import url
from django.urls import path
import django.contrib.auth.views
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
    url(r'^success$', pages.views.success, name='success'),
    url(r'^user_home$', pages.views.user_home_view, name='user_home'),
    url(r'^view_following$', pages.views.view_following, name='view_following'),
    url(r'^view_nearby$', pages.views.view_nearby, name='view_nearby'),
    url(r'^public_profile/(?P<userid>\d+)/$', pages.views.public_profile, name='public_profile'),
    url(r'^my_profile/$', pages.views.my_profile, name='my_profile'),
    url(r'^dataviewer$', pages.views.dataviewer, name='dataviewer'),
    url(r'^admin/', admin.site.urls), # admin site url
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
