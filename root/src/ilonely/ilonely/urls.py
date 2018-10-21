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
    url(r'^login$', pages.views.login, name='login'),
    url(r'^forgot_username$', pages.views.forgot_username, name='forgot_username'),
    url(r'^forgot_password$', pages.views.forgot_password, name='forgot_password'),
    url(r'^success$', pages.views.success, name='success'),
]