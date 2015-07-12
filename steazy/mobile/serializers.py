from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from models import Song, Playlist

__author__ = 'Ian'


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'name', 'artist', 'album', 'source', 'tag', 'plays', 'inherited_popularity')


class PlaylistDetailSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    song_details = serializers.SerializerMethodField()

    class Meta:
        model = Playlist

    def get_owner_name(self, obj):
        return obj.owner.username

    def get_song_details(self, obj):
        return SongSerializer(obj.songs.all(), many=True).data


class PlaylistOverviewSerializer(serializers.ModelSerializer):
    length = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ('id', 'name', 'owner', 'length')

    def get_length(self, obj):
        return obj.songs.count()


class UserSerializer(serializers.ModelSerializer):
    playlists = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.groups = [Group.objects.get(pk=1), ]
        user.save()
        return user

    class Meta:
        model = get_user_model()

    def get_playlists(self, obj):
        playlists = obj.playlist_set
        return PlaylistOverviewSerializer(playlists, many=True).data


class TokenSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'state',)

    def get_state(self, obj):
        return obj.user.spotifyuser.state