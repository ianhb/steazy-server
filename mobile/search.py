import json
import urllib2

from mobile.models import Song

__author__ = 'Ian'


def check_if_exists(song_data):
    return Song.objects.filter(source=song_data['source'], tag=song_data['tag']).exists()


def search_spotify(arguement):
    arguement = arguement.replace(' ', '+')
    data = json.load(urllib2.urlopen('https://api.spotify.com/v1/search?q=' + arguement + '%20&type=track'))
    return data


def parse_spotify(data):
    songs = []
    for track in data['tracks']['items']:
        if check_if_exists({'source': 'Spotify', 'tag': track['id']}):
            songs.append(Song.objects.get(source='Spotify', tag=track['id']))
        else:
            artists = ''
            for art in track['artists']:
                artists += art['name'] + ', '
            artists = artists[:len(artists) - 2]
            song = Song(name=track['name'], artist=artists, album=track['album']['name'],
                        source='Spotify', tag=track['id'], inherited_popularity=track['popularity'])
            song.save()
            songs.append(song)
    return songs


def sort_songs(songs):
    return sorted(songs, key=lambda song: song.inherited_popularity, reverse=True)


def search(query):
    return sort_songs(parse_spotify(search_spotify(query)))


'''
def search_soundcloud(arguement):
    # create a client object with your app credentials
    client = soundcloud.Client(client_id='YOUR_CLIENT_ID')

    # find all sounds of buskers licensed under 'creative commons share alike'
    tracks = client.get('/tracks', q=['kygo'],limit=10)
    for track in tracks:
        print track.title + " " + track.artist
'''
