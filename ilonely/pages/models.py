from django.db import models

#I believe primary keys are handling automatically
#We may need to add extra getter setter methods
#for example if a user tries to log in we need a method
#getUser(username, password) that returns a userid or 
#null or -1 if the user does not exist

class User(models.Model):
    email = models.EmailField(max_length=75)
    username = models.CharField(unique=True,max_length=50)
    password = models.CharField(max_length=75)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    bio = models.TextField()
    age = models.PositiveIntegerField()
    photo = models.ImageField(upload_to="profile_photo/", null=True, blank=True)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #apparently cascade delete happens automatically?
    postContent = models.TextField()
    datePosted = models.DateTimeField(auto_now_add=True)

class Follow(models.Model):
    userFollowing = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userFollowing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

class Thread(models.Model):
    userOne = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userOne")
    userTwo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userTwo")

class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    messageContent = models.TextField()
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    datePosted = models.DateTimeField(auto_now_add=True)