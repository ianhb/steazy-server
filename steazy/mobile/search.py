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
    """
    Class to handle maintaining the Spotify Client Credentials code to increase query request speed
    """
    def __init__(self):
        self.TOKEN_EXPIRES = calendar.timegm(time.gmtime())
        self.TOKEN = None

    def spotify_auth(self):
        """
        Gets the Client Credentials for Steazy
        :return: Spotify access token
        """
        header = spotifyviews.HEADERS
        body = {'grant_type': 'client_credentials'}

        client_request = requests.post(spotifyviews.SPOTIFYURL, data=body, headers=header)

        response = client_request.json()

        self.TOKEN_EXPIRES = self.TOKEN_EXPIRES + response['expires_in']

        return response['access_token']

    def search_spotify(self, argument):
        """
        Searches Spotify with Client Credentials
        :param argument: String to search Spotify
        :return: JSON response of tracks from Spotify. Described at https://developer.spotify.com/web-api/search-item/
        """
        if calendar.timegm(time.gmtime()) > self.TOKEN_EXPIRES:
            self.TOKEN = self.spotify_auth()
        header = {'Authorization': 'Bearer ' + self.TOKEN}
        argument = argument.replace(' ', '+')
        data = requests.get('https://api.spotify.com/v1/search?q=' + argument + '%20&type=track', headers=header)
        return data.json()

    @staticmethod
    def parse_spotify(data):
        """
        Parse JSON of list of Spotify track search results and return a list of Steazy songs associated with them.
        Doesn't create new songs if they already exist in the database
        :param data: JSON list of Spotify track results. Described at https://developer.spotify.com/web-api/search-item/
        :return:
        """
        songs = []
        for track in data:
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
        return songs


SPOTIFY = Spotify()


def check_if_exists(song_data):
    """
    Returns a song if it already exists in the database
    :param song_data: Dictionary containing song's source and tag
    :return: Song object if song exists, None otherwise
    """
    try:
        return Song.objects.get(source=song_data['source'], tag=song_data['tag'])
    except Song.DoesNotExist:
        return None


def sort_songs(songs):
    """
    Returns songs sorted in order of inherited popularity.
    To be improved once more data has been collected
    :param songs: List of Song objects
    :return: songs in order of descending popularity
    """
    return sorted(songs, key=lambda song: song.inherited_popularity, reverse=True)


def search_songs(query):
    """
    Returns a sorted list of songs from Spotify and Soundcloud
    :param query: String keyword(s) to search
    :return: List of Songs matching query
    """
    return sort_songs(Spotify.parse_spotify(SPOTIFY.search_spotify(query)['tracks']['items']) +
                      parse_soundcloud(search_soundcloud(query)))


def search_database(query):
    """
    Queries the local database to find any songs that match query
    :param query: String keyword(s) to search
    :return: List of Songs matching query
    """

    # TODO: Improve the search (ability to search multiple fields at once)
    return sort_songs(Song.objects.filter(Q(name__icontains=query) |
                                          Q(artist__icontains=query) | Q(album__icontains=query)))[0:20]


def search_soundcloud(argument):
    """
    Searches Soundcloud and returns a JSON result of songs
    :param argument: String keyword(s) to search
    :return: JSON result of search
    """
    # create a client object with your app credentials
    client = soundcloud.Client(client_id='81ca87317b91e4051f6d8797e5cce358')

    tracks = client.get('/tracks', q=argument, limit=10, encoding="utf-8")

    return tracks


def parse_soundcloud(data):
    """
    Turns a JSON response from Soundcloud into a list of Songs
    :param data: JSON response of tracks from Soundcloud
    :return: List of Songs from search
    """
    songs = []
    for track in data:
        print track.title
        song = check_if_exists({'source': 'Soundcloud', 'tag': track.id})
        if song is not None:
            songs.append(song)
        elif json.load(urllib2.urlopen('https://api.soundcloud.com/tracks/' + str(track.id) +
                                               '?client_id=81ca87317b91e4051f6d8797e5cce358'))['streamable']:
            song = Song(name=unicode(track.title), artist=unicode(track.user['username']), album='',
                        source='Soundcloud', tag=track.id,
                        inherited_popularity=track.favoritings_count / float(10000))
            song.save()
            songs.append(song)
    return songs
