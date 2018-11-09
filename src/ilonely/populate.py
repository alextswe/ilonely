from faker import Faker
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from pages.models import Profile, Post
from pages.geo import getLocation
import requests
from random import randrange
from haversine import haversine

geodata = getLocation()
execLat = geodata['latitude']
execLong = geodata['longitude']
city = geodata["city"]
state = geodata["region_code"]
fake = Faker()
users = []
profiles = []

for i in range(20):
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
    profile.location = ("%s, %s") % (city, state)
    profile.latitude = fake.geo_coordinate(execLat, radius=(0.001*10**randNum + 0.001*10**randNum2))
    profile.longitude = fake.geo_coordinate(execLong, radius=(0.001*10**randNum2 + 0.001*10**randNum))
    profile.bio = ' '.join(fake.sentences(nb=randNum+randNum2+1, ext_word_list=None))
    profile.save()
    # generate posts for users
    for _ in range(randNum):
        post = Post.objects.create(
            profile = profile,
            postContent = fake.text(max_nb_chars=50*randNum+60*randNum2+100, ext_word_list=None)
        )
        post.save()

print('Done!')