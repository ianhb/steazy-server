import base64
import os

import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from models import SpotifyUser

if 'RDS_DB_NAME' in os.environ:
    REDIRECTURI = "http://steazy-dev.elasticbeanstalk.com/user/spotifycallback"
else:
    REDIRECTURI = 'http://localhost:8000/users/spotifycallback'
CLIENT_ID = 'e0fd082de90e4cd7b60bf6047f5033f0'
CLIENT_SECRET = '227a222269bd48358f65c8e1fda0276f'
SPOTIFYURL = 'https://accounts.spotify.com/api/token'

HEADERS = {'Authorization': 'Basic ' + base64.standard_b64encode(CLIENT_ID + ':' + CLIENT_SECRET)}


@api_view(['GET', ])
@permission_classes((AllowAny,))
def auth_received(request):
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
    refresh_token = request.user.spotifyuser.refresh_token

    body = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}

    token_request = requests.post(SPOTIFYURL, data=body, headers=HEADERS)

    access_token = token_request.json()['access_token']

    return Response({'access_token': access_token}, status=status.HTTP_200_OK)


@api_view(['GET', ])
def get_state(request):
    state = request.user.spotifyuser.state
    return Response({'state': state}, status=status.HTTP_200_OK)
