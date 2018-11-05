from django.contrib.auth.models import User
from pages.models import Profiles

for i in range(50):
    user = User.objects.create_user(
            'testUser%d' % i,
            '%s%d@fakemail.com' % (fake., i)
        )