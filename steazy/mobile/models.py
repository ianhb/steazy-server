from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Playlist(models.Model):
    name = models.CharField(max_length=30)

    owner = models.ForeignKey(User)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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


class Song_to_Playlist(models.Model):
    song = models.ForeignKey(Song)

    playlist = models.ForeignKey(Playlist)

    date_added = models.DateTimeField(auto_now_add=True)

    added_by = models.ForeignKey(User)


class Play(models.Model):
    song = models.ForeignKey(Song)

    player = models.ForeignKey(User)

    date = models.DateTimeField(auto_now_add=True)
