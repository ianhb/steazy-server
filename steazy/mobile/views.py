from django.contrib.auth.models import User, AnonymousUser
from django.http import Http404

# Create your views here.
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from models import Song, Playlist, Play, Search
from search import search_songs, search_database
from serializers import SongSerializer, PlaylistDetailSerializer, UserSerializer, TokenSerializer, \
    PlaylistOverviewSerializer


class SongsList(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, format=None):
        try:
            query = request.GET.get('query')
            try:
                if request.user is AnonymousUser:
                    raise User.DoesNotExist()
                search = Search(user=request.user, query=query)
                search.save()
            except User.DoesNotExist:
                print "Anonymous Search"
            songs = search_songs(query)
            serial = SongSerializer(songs, many=True)
            return Response(serial.data, status=status.HTTP_200_OK)
        except MultiValueDictKeyError:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


class FastSongSearch(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, format=None):
        try:
            query = request.GET.get('query')
            songs = search_database(query)
            serial = SongSerializer(songs, many=True)
            return Response(serial.data, status=status.HTTP_200_OK)
        except MultiValueDictKeyError:
            return Response(request.data, status=status.HTTP_400_BAD_REQUEST)


class PlaylistList(APIView):
    def get(self, request, format=None):
        playlists = Playlist.objects.filter(owner=request.user)
        serial = PlaylistOverviewSerializer(playlists, many=True)
        return Response(serial.data)

    def post(self, request, format=None):
        request.data['owner'] = request.user.pk
        serial = PlaylistOverviewSerializer(data=request.data)
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
        serial = PlaylistDetailSerializer(playlist)
        return Response(serial.data, status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        playlist = self._get_playlist(pk)
        request_type = request.data['type']
        request_data = request.data['data']
        if request_type == 'rename':
            playlist.name = request_data
            playlist.save()
        elif request_type == 'add':
            song = Song.objects.get(pk=request_data)
            playlist.songs.add(song)
        elif request_type == 'remove':
            song = Song.objects.get(pk=request_data)
            playlist.songs.remove(song)
        serial = PlaylistDetailSerializer(playlist)
        return Response(serial.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, pk, format=None):
        playlist = self._get_playlist(pk)
        playlist.delete()
        return Response(status=status.HTTP_202_ACCEPTED)


class UserView(APIView):
    def get(self, request, format=None):
        user = request.user
        serial = UserSerializer(user)
        return Response(serial.data, status=status.HTTP_200_OK)


class CreateUser(APIView):

    permission_classes = [
        permissions.AllowAny,
    ]

    def post(self, request, format=None):
        request.data['user_permissions'] = 1
        request.data['groups'] = 1
        ser = UserSerializer(data=request.data)
        if ser.is_valid():
            if User.objects.filter(email=ser.initial_data['email']).exists():
                data = {}
                data['email'] = ['This field must be unique']
                return Response(data, status=status.HTTP_409_CONFLICT)
            user = User.objects.create_user(
                ser.initial_data['username'],
                ser.initial_data['email'],
                ser.initial_data['password']
            )
            return Response(TokenSerializer(Token.objects.get(user=user)).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayView(APIView):
    def post(self, request, format=None):
        data = request.data
        try:
            player = request.user
            song = Song.objects.get(pk=data['song'])
            play = Play(player=player, song=song)
            play.save()
            serial = SongSerializer(song)
            song.plays += 1
            song.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        except Song.DoesNotExist:
            return Response("Song PK DNE", status=status.HTTP_400_BAD_REQUEST)

