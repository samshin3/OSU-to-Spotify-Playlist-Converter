import osu_song_compiler
from dotenv import load_dotenv
import os
import spotify_functions
from flask import Flask, redirect, request, session
from favourites import *

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = "http://localhost:5000/callback"
state = spotify_functions.random_string_gen(16)


def spotify_query(token, flat_list):
    errors = []
    spotify_uris = []

    for osu_songs in flat_list:
        result = spotify_functions.search_artist(osu_songs, token)

        if result.startswith("Error"):
            errors.append(result.removeprefix("Error"))
        else:
            spotify_uris.append(result)
        if len(spotify_uris) == int(session["song_count"]):
            break
    
    search_query = ",".join(spotify_uris)

    return search_query, errors, len(spotify_uris)

app = Flask(__name__)
app.secret_key = "43j681a9-129j-0962-b936-9f1254093461"

@app.route("/")
def index():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"

@app.route("/login")
def login():

    auth_url = spotify_functions.user_auth_url(client_id,redirect_uri,state)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    
    if "error" in request.args:
        return redirect("/error")
            
    if "code" in request.args:

        if request.args["state"] != state:
            return redirect("/error")
            
        try:        
            code = request.args["code"]
            session["token"] = spotify_functions.get_token(code,client_id,client_secret,redirect_uri)
                
            return redirect("/playlistmaker")

        except KeyError:
            return redirect("/error")

@app.route("/playlistmaker")

def user_choice():

    if not session["token"]:
        return redirect("/error")
    
    while True:
        session["name"] = input("What do you want to call your playlist?")
        if not session["name"]:
            print("Please give a name, you cannot leave this field blank")
        else:
            break

    session["desc"] = input("What description will you give it (Leave blank if none)")

    while True:
        try:

            session["song_count"] = input("How many songs do you want to add?")

            if 0 < int(session["song_count"]) <= 100:
                break   
            if int(session[{"song_count"}]) > 100:
                print("You cannot compile more than 100 songs at once")
            if int(session["song_count"]) <= 0:
                print("Please enter a valid number, you must compile at least 1 song")
                        
        except ValueError:
            print("Input a whole number")
    
    session["playlist_id"] = spotify_functions.create_playlist(session["token"],userid=spotify_functions.get_user_id(session["token"]), playlist_name=session["name"], description=session["desc"])

    return "Where do you want to get your songs from?\n <a href='/playlistmaker/fromfile'>From file</a>\n <a href='/playlistmaker/fromosu'>From Osu Profile</a>"

@app.route("/playlistmaker/fromfile")
def osu_to_spotify():

    try:
        while True:
            try:
                path = r"" + input("insert the osu map folder path")
                check_path = os.listdir(path) 
                if check_path:
                    break
            except FileNotFoundError:
                print("Path not found, choose a valid path")

        songs = osu_song_compiler.compile_songs(path)
        unique_songs = osu_song_compiler.dupe_remover(songs)
        flat_list = [item for sublist in unique_songs for item in sublist] #removes sublists from main list
        
        search_query, errors, successfulsongs = spotify_query(session["token"],flat_list)
        outcome = spotify_functions.add_songs(session["token"], session["playlist_id"],search_query)

        if "snapshot_id" in outcome:

            return f"Successfully added {successfulsongs} song(s) to your new playlist\n" + f"The following songs could not be found on spotify:{errors}\n" + "click <a href='/'>here</a> to return to the home page"
        
    except (TypeError, KeyError):
        return redirect("/error") 
    
@app.route("/playlistmaker/fromosu")

def from_osu():
    
    try:
        while True:

            name =input("Input your OSU! username: ")
            try:
                osu_id = check_user(name)
                break

            except ValueError:
                print("User not found")

        while True:
    
            cat = input("Which category do you want to search for? ")
            flat_list = query_maker(osu_id,cat)
            if flat_list:
                break
            else:
                print("No beatmap found in specified category")

        search_query, errors, successfulsongs = spotify_query(session["token"], flat_list)
        outcome = spotify_functions.add_songs(session["token"], session["playlist_id"],search_query)

        if "snapshot_id" in outcome:
            return f"Successfully added {successfulsongs} song(s) to your new playlist\n" + f"The following songs could not be found on spotify:{errors}\n" + "click <a href='/'>here</a> to return to the home page" 

    except (TypeError, KeyError):
        return redirect("/error") 

@app.route("/error")

def errorhandling():
    return "There was an error handling your request click <a href='/'>here</a> to return to the home page"

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)