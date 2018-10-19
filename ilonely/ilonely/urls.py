"""
Definition of urls for ilonely.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import pages.views

urlpatterns = [
    url(r'^$', pages.views.home, name='home'),
    url(r'^register$', pages.views.register, name='register'),
    url(r'^login$', pages.views.login, name='login'),
]