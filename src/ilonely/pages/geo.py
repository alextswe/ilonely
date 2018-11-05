from math import sin, cos, sqrt
from haversine import haversine
import requests
from django.contrib.auth.models import User
from pages.models import Profile

# returns the user's location info in a dictionary
def getLocation(request):
    response = requests.get('http://api.ipstack.com/check?access_key=adb841f493ebe55b01d9d14d8992f765')
    geodata = response.json()
    print(geodata)

    return geodata
# TODO: exclude blocked userss
# returns a list of people nearby in a N mi radius
def getNearby(request, radius):
    me = request.user
    myProfile = me.profile
    profiles = Profile.objects.exclude(user = me).all()
    nearbyPeople = []

    meLoc = (myProfile.latitude, myProfile.longitude)

    if profiles is not None:
        for profile in profiles:
            userLoc = (profile.latitude, profile.longitude)
            if all(userLoc):
                if haversine(meLoc, userLoc, miles=True) < radius:
                    nearbyPeople.append(profile)

    # nearbyPeople = Profile.objects.filter(location = myProfile.location).exclude(user = me).all() 
    print(nearbyPeople)
    return nearbyPeople

'''
# personal implementation of haversine formula (distance between two points on a sphere)
def haversine(lat1, long1, lat2, long2):
    radius = 6378.137 # radius of the earth

    a = sin((lat2-lat1)/2) ** 2
    b = cos(lat1) * cos(lat2) * (sin((long2-long1)/2) ** 2)
    c = sqrt(a + b)
    return 2 * radius * asin(c)
'''

# ipstack key access_key=adb841f493ebe55b01d9d14d8992f765
# google api