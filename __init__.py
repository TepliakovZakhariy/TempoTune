from flask import Flask, render_template, url_for,redirect,request
from pymongo import MongoClient
from bson.objectid import ObjectId

uri = "mongodb+srv://yurora:vervor67vervor@cluster0.pkxylky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client['Tempotune']
users = db["users"]
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/songs")
def songs():
    return render_template("songs.html")

@app.route("/playlists")
def playlists():
    return render_template("playlists.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
