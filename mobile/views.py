from django.contrib.auth import get_user_model
from django.http import Http404

# Create your views here.
from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from mobile.models import Song, Playlist, Song_to_Playlist, Play
from mobile.search import search
from mobile.serializers import SongSerializer, PlaylistSerializer, UserSerializer


class SongsList(APIView):
    def _contains(self, data):
        source = data['source']
        tag = data['tag']
        return Song.objects.filter(source=source, tag=tag).exists()

    def get(self, request, format=None):
        songs = search(request.data['query'])
        serial = SongSerializer(songs, many=True)
        return Response(serial.data)


class PlaylistList(APIView):
    def get(self, request, format=None):
        playlists = Playlist.objects.all()
        serial = PlaylistSerializer(playlists, many=True)
        return Response(serial.data)

    def post(self, request, format=None):
        serial = PlaylistSerializer(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaylistDetail(APIView):
    def _get_playlist(self, pk):
        try:
            return Playlist.objects.get(pk=pk)
        except Playlist.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        playlist = self._get_playlist(pk)
        serial = PlaylistSerializer(playlist)
        songs = playlist.song_to_playlist_set.all()
        return Response(serial.data)


class UserList(APIView):
    def get(self, request, format=None):
        users = get_user_model().objects.all()
        serial = UserSerializer(users, many=True)
        return Response(serial.data)


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer


class UserDetail(APIView):
    def _get_user(self, pk):
        try:
            return get_user_model().objects.get(pk=pk)
        except get_user_model().DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self._get_user(pk)
        serial = UserSerializer(user)
        return Response(serial.data)


class PlayView(APIView):
    def post(self, request, format=None):
        data = request.data
        try:
            player = get_user_model().objects.get(pk=data['user'])
            song = Song.objects.get(pk=data['song'])
            play = Play(player=player, song=song)
            play.save()
            serial = SongSerializer(song)
            song.plays += 1
            song.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        except get_user_model().DoesNotExist:
            return Response("User PK DNE", status=status.HTTP_400_BAD_REQUEST)
        except Song.DoesNotExist:
            return Response("Song PK DNE", status=status.HTTP_400_BAD_REQUEST)


class AddToPlaylistView(APIView):
    def post(self, request, format=None):
        data = request.data
        try:
            playlist = Playlist.objects.get(pk=data['playlist'])
            song = Song.objects.get(pk=data['song'])
            user = get_user_model().objects.get(pk=data['added_by'])
            add = Song_to_Playlist(added_by=user, playlist=playlist, song=song)
            add.save()
            return Response(data, status=status.HTTP_201_CREATED)
        except Playlist.DoesNotExist:
            return Response("Playlist PK DNE", status=status.HTTP_400_BAD_REQUEST)
        except Song.DoesNotExist:
            return Response("Song PK DNE", status=status.HTTP_400_BAD_REQUEST)
        except get_user_model().DoesNotExist:
            return Response("User PK DNE", status=status.HTTP_400_BAD_REQUEST)
