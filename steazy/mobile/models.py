from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

# Create your models here.
class Playlist(models.Model):
    name = models.CharField(max_length=30)

    owner = models.ForeignKey(User)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u"%s" % self.name


class Song(models.Model):
    SOURCES = [
        ('Spotify', 'SPO'),
        ('Soundcloud', 'SOU')
    ]

    name = models.CharField(max_length=255)

    artist = models.CharField(max_length=255)

    album = models.CharField(max_length=255)

    source = models.CharField(choices=SOURCES, max_length=20)

    tag = models.CharField(max_length=30)

    date_added = models.DateTimeField(auto_now_add=True)

    plays = models.IntegerField(default=0)

    inherited_popularity = models.FloatField()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u"%s" % self.name


class Song_to_Playlist(models.Model):
    song = models.ForeignKey(Song)

    playlist = models.ForeignKey(Playlist)

    date_added = models.DateTimeField(auto_now_add=True)

    added_by = models.ForeignKey(User)


class Play(models.Model):
    song = models.ForeignKey(Song)

    player = models.ForeignKey(User)

    date = models.DateTimeField(auto_now_add=True)


class Search(models.Model):
    time = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User)

    query = models.CharField(max_length=255)

    def __unicode__(self):
        return u"%s" % self.query
