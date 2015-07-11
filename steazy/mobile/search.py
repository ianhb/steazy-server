import calendar
import json
import urllib2
import time

from django.db.models import Q
import requests
import soundcloud as soundcloud

from models import Song
import spotifyviews

__author__ = 'Ian'


class Spotify:
    def __init__(self):
        self.TOKEN_EXPIRES = calendar.timegm(time.gmtime())
        self.TOKEN = None

    def spotify_auth(self):
        header = spotifyviews.HEADERS
        body = {'grant_type': 'client_credentials'}

        client_request = requests.post(spotifyviews.SPOTIFYURL, data=body, headers=header)

        response = client_request.json()

        self.TOKEN_EXPIRES = self.TOKEN_EXPIRES + response['expires_in']

        return response['access_token']

    def search_spotify(self, argument):
        if calendar.timegm(time.gmtime()) > self.TOKEN_EXPIRES:
            self.TOKEN = self.spotify_auth()
        header = {'Authorization': 'Bearer ' + self.TOKEN}
        argument = argument.replace(' ', '+')
        data = requests.get('https://api.spotify.com/v1/search?q=' + argument + '%20&type=track', headers=header)
        return data.json()

    @staticmethod
    def parse_spotify(data):
        songs = []
        for track in data['tracks']['items']:
            if check_if_exists({'source': 'Spotify', 'tag': track['id']}):
                songs.append(Song.objects.get(source='Spotify', tag=track['id']))
            else:
                artists = ''
                for art in track['artists']:
                    artists += unicode(art['name']) + ', '
                artists = artists[:len(artists) - 2]
                song = Song(name=unicode(track['name']), artist=artists, album=unicode(track['album']['name']),
                            source='Spotify', tag=track['id'], inherited_popularity=track['popularity'])
                song.save()
                songs.append(song)
        return songs


SPOTIFY = Spotify()

def check_if_exists(song_data):
    return Song.objects.filter(source=song_data['source'], tag=song_data['tag']).exists()


def sort_songs(songs):
    return sorted(songs, key=lambda song: song.inherited_popularity, reverse=True)


def search_songs(query):
    return sort_songs(Spotify.parse_spotify(SPOTIFY.search_spotify(query)) + parse_soundcloud(search_soundcloud(query)))


def search_database(query):
    return sort_songs(Song.objects.filter(Q(name__icontains=query) |
                                          Q(artist__icontains=query) | Q(album__icontains=query)))[0:20]


def search_soundcloud(argument):
    # create a client object with your app credentials
    client = soundcloud.Client(client_id='81ca87317b91e4051f6d8797e5cce358')

    # find all sounds of buskers licensed under 'creative commons share alike'
    tracks = client.get('/tracks', q=argument, limit=10, encoding="utf-8")

    return tracks


def parse_soundcloud(data):
    songs = []
    for track in data:
        print track.title
        if track.streamable and check_if_exists({'source': 'Soundcloud', 'tag': track.id}):
            songs.append(Song.objects.get(source='Soundcloud', tag=track.id))
        elif json.load(urllib2.urlopen('https://api.soundcloud.com/tracks/' + str(track.id) +
                                               '?client_id=81ca87317b91e4051f6d8797e5cce358'))['streamable']:
            song = Song(name=unicode(track.title), artist=unicode(track.user['username']), album='',
                        source='Soundcloud', tag=track.id,
                        inherited_popularity=track.favoritings_count / float(10000))
            song.save()
            songs.append(song)
    return songs
