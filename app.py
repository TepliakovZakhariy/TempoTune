from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from random import getrandbits
from datetime import datetime
from ast import literal_eval
import random

uri = "mongodb+srv://yurora:tempotune123official@cluster0.pkxylky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client['TempoTune']
users = db["users"]
temp = db["temp"]
app = Flask(__name__)
app.secret_key=['very_secret']
spotify_client=spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="f17426cd426c406eb0909cb148cb0981",client_secret='3b0ee8a224654b54bb417f35cbda9e01'))

def milliseconds_to_string_duration(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    duration_string = "{:02}:{:02}".format(minutes, seconds)

    if hours > 0:
        duration_string = "{:02}:{:02}".format(hours, duration_string)

    return duration_string

class Song:
    def __init__(self, name, artist, album, url, album_url, artist_url, duration,
                 preview_url, cover_big, cover_medium, cover_small):
        self.name = name
        self.artist = artist
        self.album=album
        self.url = url
        self.album_url = album_url
        self.artist_url = artist_url
        self.duration = duration
        self.preview_url = preview_url
        self.cover_big = cover_big
        self.cover_medium = cover_medium
        self.cover_small = cover_small

    def __repr__(self):
        return f'{self.name} by {self.artist}'

class Playlist:
    def __init__(self, track, limit, instrumentalness, energy, danceability, valence, popularity, acousticness):
        self.name = None
        self.id = getrandbits(64)
        self.songs = []
        self.total_duration=0
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = datetime.now().year
        self.date = f'{current_day}.{current_month}.{current_year}'
        if track is False:
            genres=spotify_client.recommendation_genre_seeds()['genres']
            genres=[random.choice(genres)]
            recomendations = spotify_client.recommendations(seed_genres=genres, limit=100, target_instrumentalness=instrumentalness, target_energy=energy, target_danceability=danceability, target_valence=valence, target_popularity=popularity, target_acousticness=acousticness)
        else:
            recomendations = spotify_client.recommendations(seed_tracks=[track], limit=100, target_instrumentalness=instrumentalness, target_energy=energy, target_danceability=danceability, target_valence=valence, target_popularity=popularity, target_acousticness=acousticness)
        recomendations = recomendations['tracks']
        for track in recomendations:
            if not track['preview_url']:
                continue
            name = track['name']
            artist = ', '.join([artist['name'] for artist in track['artists']])
            album = track['album']['name']
            url = track['external_urls']['spotify']
            album_url = track['album']['external_urls']['spotify']
            artist_url = track['artists'][0]['external_urls']['spotify']
            duration = track['duration_ms']
            self.total_duration+=duration
            duration=milliseconds_to_string_duration(duration)
            preview_url = track['preview_url']
            try:
                cover_big = track['album']['images'][0]['url']
                cover_medium = track['album']['images'][1]['url']
                cover_small = track['album']['images'][2]['url']
            except IndexError:
                print('ERROR: No cover found')
                cover_big = None
                cover_medium = None
                cover_small = None
            song = Song(name, artist, album, url, album_url, artist_url, duration, preview_url,
                        cover_big, cover_medium, cover_small)
            self.songs.append(song.__dict__)
        self.total_duration=milliseconds_to_string_duration(self.total_duration)
        self.songs = self.songs[:limit]
        if len(self.songs) < limit:
            print('ERROR: Not enough songs to fill the playlist')

    def __str__(self):
        return repr(self.__dict__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if "email" in session:
        return redirect(url_for('playlists'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        f_user=users.find_one({'email':email})
        if not username or not email or not password:
            message = 'All fields are required'
            return render_template('login.html', message=message)
        if not f_user:
            message = 'User with such email does not exist'
            return render_template('login.html', message=message)
        if f_user['username']!=username or f_user['password']!=password:
            message = 'Wrong username or password'
            return render_template('login.html', message=message)
        session["email"]=email
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if "email" in session:
        return redirect(url_for('playlists'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not username or not email or not password:
            message = 'All fields are required'
            return render_template('signup.html', message=message)
        if users.find_one({'email':email}):
            message = 'User with such email already exists'
            return render_template('signup.html', message=message)
        users.insert_one(
            {'username': username, 'email': email, 'password': password, 'playlists': []})
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/playlists')
def playlists():
    user = users.find_one({"email" : session["email"]})
    name = user['username']
    playlists_ = user['playlists']
    playlists_ = [literal_eval(playlist) for playlist in playlists_]
    return render_template('playlists.html', name=name, playlists=playlists_)


@app.route('/songs/<playlist_id>')
def songs(playlist_id):
    playlists_ = users.find_one({"email" : session["email"]})['playlists']
    playlists_ = [literal_eval(playlist) for playlist in playlists_]
    playlist = [playlist for playlist in playlists_ if playlist['id'] == int(playlist_id)][0]
    return render_template('songs.html', playlist=playlist)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if "email" in session:
        session.pop("email", None)
    return render_template("index.html")


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        if request.form['action']=='generate':
            song = request.form['song']
            if not song:
                song = False
            else:
                if 'open.spotify.com' not in song:
                    song = spotify_client.search(q=song, type='track')['tracks']['items'][0]['external_urls']['spotify']
            song_amount = request.form['song_amount']
            if not song_amount:
                song_amount = 25
            if int(song_amount) > 50:
                song_amount = 50
            if int(song_amount) < 1:
                song_amount = 1
            song_amount = int(song_amount)
            instrumentalness = int(request.form['instrumentalness'])*0.01 if request.form['instrumentalness']!='0.5' else None
            energy = int(request.form['energy'])*0.01 if request.form['energy']!='0.5' else None
            danceability = int(request.form['danceability'])*0.01 if request.form['danceability']!='0.5' else None
            valence = int(request.form['valence'])*0.01 if request.form['valence']!='0.5' else None
            popularity = int(request.form['popularity']) if request.form['popularity']!='50' else None
            acousticness = int(request.form['acousticness'])*0.01 if request.form['acousticness']!='0.5' else None
            playlist = Playlist(song, song_amount, instrumentalness, energy, danceability, valence, popularity, acousticness)
            return render_template('generate.html', playlist=playlist)
        elif request.form['action']=='reset':
            song = request.form['song']
            song_amount = request.form['song_amount']
            return render_template('generate.html', song=song, song_amount=song_amount)
    return render_template('generate.html')

@app.route('/add_playlist', methods=['GET','POST'])
def add_playlist():
    if request.method == 'POST':
        playlist=request.form['play']
        if playlist is None:
            print('ERROR: No playlist to add')
            return redirect(url_for('generate'))
        playlist=literal_eval(playlist)
        playlist_name=request.form['playlist_name']
        if not playlist_name:
            playlist_name='Playlist'
        playlist['name']=playlist_name
        playlist=str(playlist)
        user = users.find_one({"email" : session["email"]})
        user['playlists'].append(playlist)
        users.update_one({"email" : session["email"]}, {"$set": {"playlists": user['playlists']}})
        return redirect(url_for('playlists'))
    else:
        print('ERROR: Not a POST request')

@app.route('/reset_options', methods=['GET','POST'])
def reset_options():
    return render_template('generate.html')

@app.route('/delete_playlist/<playlist_id>', methods=['GET','POST'])
def delete_playlist(playlist_id):
    user = users.find_one({"email" : session["email"]})
    playlists_ = user['playlists']
    playlists_ = [literal_eval(playlist) for playlist in playlists_]
    playlist = [playlist for playlist in playlists_ if playlist['id'] == int(playlist_id)][0]
    playlists_.remove(playlist)
    playlists_ = [str(playlist) for playlist in playlists_]
    users.update_one({"email" : session["email"]}, {"$set": {"playlists": playlists_}})
    return redirect(url_for('playlists'))

if __name__ == '__main__':
    app.run(debug=True)
