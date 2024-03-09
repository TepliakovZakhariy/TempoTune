from flask import Flask, render_template

app = Flask(__name__)


@app.route("/songs")
def index():
    return render_template("songs.html")

@app.route("/playlists")
def playlists():
    return render_template("playlists.html")

if __name__ == "__main__":
    app.run(debug=True)
