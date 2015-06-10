from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from mobile.models import Song, Playlist, Song_to_Playlist

__author__ = 'Ian'


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'name', 'artist', 'album', 'source', 'tag', 'plays', 'inherited_popularity')


class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ('id', 'name', 'owner_name', 'owner', 'date_created', 'songs',)

    def get_songs(self, obj):
        songs = obj.song_to_playlist_set
        return SongtoPlaylistSerializer(songs, many=True).data

    def get_owner_name(self, obj):
        return obj.owner.username


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
        return PlaylistSerializer(playlists, many=True).data


class SongtoPlaylistSerializer(serializers.ModelSerializer):
    song_data = serializers.SerializerMethodField()

    class Meta:
        model = Song_to_Playlist
        fields = ('song_data',)

    def get_song_data(self, obj):
        song = obj.song
        return SongSerializer(song).data
