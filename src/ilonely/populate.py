from faker import Faker
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from pages.models import Profile, Post
from pages.geo import getLocation
from random import randrange
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import requests
import sys

user = User.objects.get(username='msant')
profile = user.profile
myLoc = profile.location
execLat = profile.latitude
execLong = profile.longitude


fake = Faker()
users = []
profiles = []
geolocator = Nominatim(user_agent="ilonely")

for i in range(4):
    # generate users
    randNum = randrange(1,3)
    randNum2 = randrange(0,2)
    
    user = User(
        username = 'testUser%d' % i,
        email = '%s%d@testmail.com' % (fake.word(ext_word_list=None), i),
        password = make_password('12345'),
        first_name = fake.first_name(),
        last_name = fake.last_name(),
    ) 
    user.save()
    # generate profile for users
    profile = user.profile    
    profile.latitude = fake.geo_coordinate(execLat, radius=(0.001*10**randNum + 0.001*10**randNum2))
    profile.longitude = fake.geo_coordinate(execLong, radius=(0.001*10**randNum2 + 0.001*10**randNum))
    gotLoc = False
    while not gotLoc:
        try:
            location = geolocator.reverse("%s, %s" % (profile.latitude, profile.longitude))
            gotLoc = True
        except GeocoderTimedOut:
            gotLoc = False
    geodata = location.raw
    state = geodata['address']['state']
    profile.location = myLoc
    try:
        if geodata['address']['city'] is not None:
            city = (geodata['address']['city'])
            profile.location = ("%s, %s") % (city, state)
    except:
        if geodata['address']['hamlet']:
            city = (geodata['address']['hamlet'])
            profile.location = ("%s, %s") % (city, state)
    profile.bio = ' '.join(fake.sentences(nb=randNum+randNum2+1, ext_word_list=None))
    profile.age = randrange(18,40)
    profile.save()
    # generate posts for users
    for _ in range(randNum):
        post = Post.objects.create(
            profile = profile,
            postContent = fake.text(max_nb_chars=50*randNum+60*randNum2+100, ext_word_list=None)
        )
        post.save()

print('Done!')