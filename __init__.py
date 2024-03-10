from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

uri = "mongodb+srv://yurora:vervor67vervor@cluster0.pkxylky.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client['TempoTune']
users = db["users"]
app = Flask(__name__)

# class User:
#     """a"""
#     def __init__(self,u_id,name,email,password) -> None:
#         self.id = u_id
#         self.name=name
#         self.email=email
#         self.password=password
#         playlists = []
#     def __str__(self) -> str:
#         return f'{self.name} : '
# class 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        email = request.form['email']
        password = request.form['password']
        users.insert_one({'username': username, 'email': email, 'password': password})
        return redirect(url_for('index'))
    return render_template('login.html')
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/playlists')
def playlists():
    return render_template('playlists.html')

@app.route('/songs')
def songs():
    return render_template('songs.html')

@app.route('/generate')
def generate():
    return render_template('generate.html')

if __name__ == '__main__':
    app.run(debug=True)