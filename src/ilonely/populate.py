from faker import Faker
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from pages.models import Profile, Post
from pages.geo import getLocation
import requests
from random import randrange

geodata = getLocation()
execLat = geodata['latitude']
execLong = geodata['longitude']
city = geodata["city"]
state = geodata["region_code"]
fake = Faker()
users = []
profiles = []

for i in range(5):
    # generate users
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
    profile.latitude = fake.geo_coordinate(execLat, radius=0.001)
    profile.longitude = fake.geo_coordinate(execLong, radius=0.001)
    profile.bio = ' '.join(fake.sentences(nb=3, ext_word_list=None))
    profile.save()
    # generate posts for users
    for _ in range(randrange(1,3)):
        post = Post.objects.create(
            profile = profile,
            postContent = fake.text(max_nb_chars=200, ext_word_list=None)
        )
        post.save()

print('Done!')