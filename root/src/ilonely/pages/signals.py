from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.gis.geoip2 import GeoIP2
from pages.models import Profile

# Profile is created when a user is created
@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):
    # Do not create profile for superuser or staff
    if not instance.is_superuser and not instance.is_staff:
        if created:
            profile = Profile.objects.create(user=instance)
            profile.save()

# Location is set/updated whenever the sender logs in
@receiver(user_logged_in, sender=User)
def setLocation(sender, request, user, **kwargs):
    # Checks if user a superuser or staff
    if not user.is_superuser and not user.is_staff:
        userLocDict = getLocation(request)
        city = userLocDict["city"]
        state = userLocDict["region"]

        # Search for user's profile
        profile = Profile.objects.filter(user=user).first()
        profile.location = ("%s, %s") % (city, state)
        profile.save()

# Helper functions
# returns the user's location info in a dictionary
def getLocation(request):
    g = GeoIP2()
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        # Hard coded IP address that points to Riverside
        ip = '97.90.192.237'

    return g.city(ip)