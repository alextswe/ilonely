from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen
from io import BytesIO

# custom authentication pipeline step to set user profile
def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        profile = user.profile;

        # set username to first part of email
        user.username=user.username.split(".")[0]

        # Code grabbed from https://stackoverflow.com/a/29576422 to set profile picture from a url
        # set profile picture from google picture if it exists
        if response['image']['url'] is not None and not(response['image']['isDefault']):
            img_url = response['image']['url']
            content = urlopen(img_url)
            io = BytesIO(content.read())
            profile.photo.save('profile_pic_{}.jpg'.format(user.pk), File(io))
            profile.save()

        print(response)
