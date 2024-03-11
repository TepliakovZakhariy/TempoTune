from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

uri = "mongodb+srv://yurora:tempotune123official@cluster0.pkxylky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client['TempoTune']
users = db["users"]
app = Flask(__name__)

spotify_client=spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="f17426cd426c406eb0909cb148cb0981",client_secret='0f16e1667986460c9841c0aa0944415a'))

def milliseconds_to_string_duration(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    duration_string = "{:02}:{:02}".format(minutes, seconds)

    if hours > 0:
        duration_string = "{:02}:{:02}".format(hours, duration_string)

    return duration_string

class Song:
    def __init__(self, name, artist, url, duration,
                 preview_url, cover_big, cover_medium, cover_small):
        self.name = name
        self.artist = artist
        self.url = url
        self.duration = duration
        self.preview_url = preview_url
        self.cover_big = cover_big
        self.cover_medium = cover_medium
        self.cover_small = cover_small

    def __repr__(self):
        return f'{self.name} by {self.artist}'

class Playlist:
    def __init__(self, track):
        self.songs = []
        self.total_duration=0
        recomendations = spotify_client.recommendations(seed_tracks=[track])
        recomendations = recomendations['tracks']
        for track in recomendations:
            name = track['name']
            artist = ', '.join([artist['name'] for artist in track['artists']])
            url = track['external_urls']['spotify']
            duration = track['duration_ms']
            self.total_duration+=duration
            duration=milliseconds_to_string_duration(duration)
            preview_url = track['preview_url']
            cover_big = track['album']['images'][0]['url']
            cover_medium = track['album']['images'][1]['url']
            cover_small = track['album']['images'][2]['url']
            song = Song(name, artist, url, duration, preview_url,
                        cover_big, cover_medium, cover_small)
            self.songs.append(song)
        self.total_duration=milliseconds_to_string_duration(self.total_duration)

    def __repr__(self):
        return f'{self.total_duration}{[(song.url, song.duration) for song in self.songs]}'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        users.insert_one(
            {'username': username, 'email': email, 'password': password})
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        users.insert_one(
            {'username': username, 'email': email, 'password': password})
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/playlists')
def playlists():
    return render_template('playlists.html')


@app.route('/songs')
def songs():
    return render_template('songs.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        song = request.form['song']
        if 'open.spotify.com' not in song:
            song = spotify_client.search(q=song, type='track')['tracks']['items'][0]['external_urls']['spotify']
        playlist = Playlist(song)
        return render_template('generate.html', playlist=playlist)
    return render_template('generate.html')


if __name__ == '__main__':
    app.run(debug=True)
