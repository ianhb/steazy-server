import base64
import os

import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from models import SpotifyUser, Playlist, Song
from search import check_if_exists
from serializers import PlaylistDetailSerializer

__author__ = 'Ian'

if 'RDS_DB_NAME' in os.environ:
    REDIRECTURI = "http://steazy-dev.elasticbeanstalk.com/users/spotifycallback"
else:
    REDIRECTURI = 'http://localhost:8000/users/spotifycallback'
CLIENT_ID = 'e0fd082de90e4cd7b60bf6047f5033f0'
CLIENT_SECRET = '227a222269bd48358f65c8e1fda0276f'
SPOTIFYURL = 'https://accounts.spotify.com/api/token'
SPOTIFYAPI = 'https://api.spotify.com/v1'

HEADERS = {'Authorization': 'Basic ' + base64.standard_b64encode(CLIENT_ID + ':' + CLIENT_SECRET)}


@api_view(['GET', ])
@permission_classes((AllowAny,))
def auth_received(request):
    """
    Callback function for Spotify that is called after a user gives approval.
    Stores the authorization code and refresh token to make future logins fast
    :param request: callback from spotify
    :return: the response from Spotify after requesting an access token
    """
    # Get Callback from Spotify
    state = request.query_params['state']
    auth_code = request.query_params['code']

    user_spot = SpotifyUser.objects.get(state=state)
    user_spot.authorization_code = auth_code

    # Build request to get refresh token
    auth_data = {'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': REDIRECTURI}

    token_request = requests.post(SPOTIFYURL, data=auth_data, headers=HEADERS)

    token_request = token_request.json()

    refresh_token = token_request['refresh_token']

    user_spot.refresh_token = refresh_token
    user_spot.save()

    return Response(token_request)


@api_view(['GET', ])
def get_access_token(request):
    """
    Returns an access token for a user that has given authorization for Spotify
    :param request: request with Steazy token
    :return: Spotify access token
    """

    # TODO: Handle request if user has not given Spotify authentication
    refresh_token = request.user.spotifyuser.refresh_token

    body = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    token_request = requests.post(SPOTIFYURL, data=body, headers=HEADERS)

    access_token = token_request.json()['access_token']

    return Response({'access_token': access_token}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def get_state(request):
    """
    Gets the state (id) associated with request.user so spotifyviews.auth_received()
    is able to identify user
    :param request: request with Steazy token
    :return: state that will allow callback to identify user
    """
    state = request.user.spotifyuser.state
    return Response({'state': state}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def get_spotify_playlists(request):
    """
    Gets the user's playlists from Spotify and recreates them as Steazy playlists
    Precondition: User must have given Spotify authorization to Steazy
    :param request: request with Steazy token
    :return: list of user's new playlists
    """
    refresh_token = request.user.spotifyuser.refresh_token

    body = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    token_request = requests.post(SPOTIFYURL, data=body, headers=HEADERS)

    access_token = token_request.json()['access_token']

    api_headers = {'Authorization': 'Bearer ' + access_token}

    user_profile = requests.get(SPOTIFYAPI + "/me", headers=api_headers)

    user_id = user_profile.json()['id']

    query_params = {'limit': '50'}
    playlist_resp = requests.get(SPOTIFYAPI + "/users/" + user_id + '/playlists', headers=api_headers,
                                 params=query_params)

    playlists = playlist_resp.json()['items']

    playlist_list = []
    for playlist in playlists:
        name = playlist['name']
        href = playlist['tracks']['href']
        length = playlist['tracks']['total']

        playlist = get_playlist(request.user, name)
        playlist_list.append(playlist)

        songs = []
        adds = playlist.songs.all()
        for i in range(length / 100):
            params = {'offset': i * 100}
            playlist_tracks = requests.get(href, headers=api_headers, params=params).json()
            for item in playlist_tracks['items']:
                track = item['track']
                if track['id'] is None:
                    continue
                song = check_if_exists({'source': 'Spotify', 'tag': track['id']})
                if song is not None:
                    songs.append(song)
                else:
                    artists = ''
                    for art in track['artists']:
                        artists += unicode(art['name']) + ', '
                    artists = artists[:len(artists) - 2]
                    song = Song(name=unicode(track['name']), artist=artists, album=unicode(track['album']['name']),
                                source='Spotify', tag=track['id'], inherited_popularity=track['popularity'])
                    song.save()
                    songs.append(song)
                in_set = False
                for add in adds:
                    if add.song.__eq__(song):
                        in_set = True
                if not in_set:
                    playlist.songs.add(song)

    playlist_serial = PlaylistDetailSerializer(playlist_list, many=True)
    return Response(playlist_serial.data, status=status.HTTP_200_OK)


def get_playlist(user, name):
    """
    Checks to see if the user has a playlist named name
    If not, create the playlist
    :param user: User object
    :param name: String of name of playlist
    :return: Playlist owned by user, named name
    """
    search = Playlist.objects.filter(name=name, owner=user)
    if search.exists():
        return search[0]
    else:
        playlist = Playlist(owner=user, name=name)
        playlist.save()
        return playlist
