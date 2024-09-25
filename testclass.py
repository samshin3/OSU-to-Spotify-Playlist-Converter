from spotifyclass import Session, SpotifyAPI
from flask import Flask, redirect, request, session
from osu_song_compiler import compile_songs
import favourites

app = Flask(__name__)
app.secret_key = "43j681a9-129j-0962-b936-9f1254093461"

@app.route("/")
def index():
    return redirect(Session.get_auth_url())

@app.route("/callback")
def code():
    token = Session(request.args["code"],request.args["state"])
    session["auth"] = token.auth
    session["token"] = token.token
    session["user_spotify_id"] = SpotifyAPI.get_user_id(session["auth"]).result
    return redirect("/option")

@app.route("/option")
def options():
    return "<a href='/osusession'>Make Playlist from OSU website</a> or <a href='/filesession'>Make from file</a>"

@app.route("/filesession")
def function():
    songs = compile_songs("Songs")
    errors, track_query = SpotifyAPI.get_uris(songs, session["auth"])

    playlist = SpotifyAPI.create_playlist(session["user_spotify_id"],"Test","description", session["token"])

    SpotifyAPI.add_songs(playlist.result,track_query,session["token"])

    success = len(track_query.split(","))

    return f"Successfully added {success} song(s). Could not add the following songs: {errors}"

@app.route("/osusession")
def osusession():
    osu_id = favourites.check_user("Cookchomper")
    favourite_tracks = favourites.query_maker(osu_id,"favourite")
    errors, track_query = SpotifyAPI.get_uris(favourite_tracks, session["auth"])

    playlist = SpotifyAPI.create_playlist(session["user_spotify_id"],"Test","description", session["token"])

    SpotifyAPI.add_songs(playlist.result,track_query,session["token"])
    success = len(track_query.split(","))

    return f"Successfully added {success} song(s). Could not add the following songs: {errors}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 