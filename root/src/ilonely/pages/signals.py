from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from pages.models import Profile

# Profile is created when a user is created
@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        profile.save()

# Location is set/updated whenever the sender logs in
# @reciever()
# def setLocation(sender):
#