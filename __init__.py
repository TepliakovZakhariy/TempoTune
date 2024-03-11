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
            song = spotify
        return render_template('generate.html', song=song, artist=artist, genre=genre, bpm=bpm, key=key)

    return render_template('generate.html')


if __name__ == '__main__':
    app.run(debug=True)
