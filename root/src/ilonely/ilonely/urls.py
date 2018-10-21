"""
Definition of urls for ilonely.
"""

from datetime import datetime
from django.conf.urls import url
from django.urls import path
import django.contrib.auth.views

import pages.views

urlpatterns = [
    url(r'^$', pages.views.home, name='home'),
    url(r'^register$', pages.views.register, name='register'),
    url(r'^login$', pages.views.login_view, name='login'),
    url(r'^forgot_username$', pages.views.forgot_username_view, name='forgot_username'),
    url(r'^forgot_password$', pages.views.forgot_password_view, name='forgot_password'),
    url(r'^success$', pages.views.success, name='success'),
    url(r'^user_home$', pages.views.user_home_view, name='user_home'),
]