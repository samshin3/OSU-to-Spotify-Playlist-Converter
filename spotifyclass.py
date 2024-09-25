import base64
from requests import post,get
import json
import random
import string
import urllib.parse
from dotenv import load_dotenv
import os

def random_string_gen(length):

    letters = string.ascii_letters
    random_string = "".join(random.choice(letters) for _ in range(length))
    return random_string

class Session:

    load_dotenv()

    __client_id = os.getenv("SPOTIFY_CLIENT_ID")
    __client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    __state = random_string_gen(16)
    __redirect_uri = "http://localhost:5000/callback"
    __scope = "user-read-private user-read-email playlist-modify-public playlist-modify-private"

    def __init__(self,code,state):

        self.token = Session.get_token(code, self)
        self.auth = {"Authorization": "Bearer " + self.token}
        self.returnstate = state

    @property
    def token(self):
        return self._token
    
    @token.setter
    def token(self, result):
        if "error" in result:
            raise KeyError(result["error_description"])
        elif "access_token" in result:
            self._token = result["access_token"]
        else:
            raise KeyError("Invalid Session")
    
    @property
    def returnstate(self):
        return self._returnstate
    
    @returnstate.setter
    def returnstate(self, state):
        if state != self.__state:
            raise KeyError("Invalid State")

    #get authorization url
    @classmethod
    def get_auth_url(cls):
        params = {
            "client_id":cls.__client_id,
            "response_type": "code",
            "redirect_uri": cls.__redirect_uri,
            "state": cls.__state,
            "scope": cls.__scope,
        }
        return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    
    #get token
    @staticmethod
    def get_token(code, instance):
        url = "https://accounts.spotify.com/api/token"
        auth_string = instance.__client_id + ":" + instance.__client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        data = {
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":instance.__redirect_uri
        }
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        result = post(url,headers=headers,data=data)
        json_result = json.loads(result.content)

        return json_result

class SpotifyAPI:

    def __init__(self, function = None, reqresult=None):
        if function and reqresult:
            self.function = function
            self.result = reqresult
    
    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self, reqresult):
        if "error" in reqresult:
            raise KeyError(reqresult["error"]["message"])
        
        match self.function:
            case "get_user_id"|"create_playlist":
                self._result = reqresult["id"]

            case "add_songs":
                self._result = reqresult["snapshot_id"]

            case "search_track":
                if reqresult["tracks"]["total"] == 0:
                    self._result = "No track found"
                else:
                    self._result = reqresult["tracks"]["items"][0]["uri"]

    #Gets user id
    @classmethod
    def get_user_id(cls, auth):
        url = "https://api.spotify.com/v1/me"
        headers = auth
        result = get(url, headers=headers)
        json_result = json.loads(result.content)

        return cls("get_user_id", json_result)
    
    #creates a playlist "OSU playlist" and returns it's id for use when adding tracks to this playlist
    @classmethod
    def create_playlist(cls,userid,playlist_name,description,token):

        url = f"https://api.spotify.com/v1/users/{userid}/playlists"
        headers= {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
            }
        data = json.dumps({
        "name": playlist_name,
        "description": description,
        "public": "false"
        })
        result = post(url,headers=headers, data=data)
        json_result = json.loads(result.content)
        
        return cls("create_playlist",json_result)

    @classmethod
    #Searches the artist and track
    def search_track(cls,artist,track,auth):

        name = f"artist:{artist} track:{track}"
        query = urllib.parse.quote(name)
        url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1&offset=0"
        headers = auth

        result = get(url, headers=headers)
        json_result = json.loads(result.content)

        return cls("search_track", json_result)

        
    @classmethod
    #adds tracks into the playlist
    def add_songs(cls,id,tracks,token):
        
        #formats tracks for url
        uris = urllib.parse.quote(tracks)
        url = f"https://api.spotify.com/v1/playlists/{id}/tracks?uris={uris}"
        headers= {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
            }
        data = json.dumps({
            "uris": [
                "string"
            ],
            "position": 0
        })
        result = post(url, headers=headers, data=data) 
        json_result = json.loads(result.content)
        
        return cls("add_songs", json_result)

    @staticmethod
    def get_uris(songlist,auth):
        error_list = []
        spotify_uris = []
        for song in songlist:
            artist, track = song.split("-")
            track_id = SpotifyAPI.search_track(artist,track,auth)

            if track_id.result == "No track found":
                error_list.append(artist + track)
            else:
                spotify_uris.append(track_id.result)
    
        track_query = ",".join(spotify_uris)
        
        return error_list, track_query
