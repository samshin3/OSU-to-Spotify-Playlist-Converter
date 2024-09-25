import base64
from requests import post,get
import json
import random
import string
import urllib.parse

def random_string_gen(length):

    letters = string.ascii_letters
    random_string = "".join(random.choice(letters) for _ in range(length))
    return random_string

def user_auth_url(client_id, redirect_uri, state):

    scope = "user-read-private user-read-email playlist-modify-public playlist-modify-private"

    params = {
        "client_id":client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": scope,
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return auth_url

def get_token(code, client_id, client_secret, redirect_uri):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":redirect_uri
    }
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = post(url,headers=headers,data=data)
    json_result = json.loads(result.content)

    if "error" in json_result:
        raise KeyError
    
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_user_id(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    if "error" in json_result:
        raise KeyError
    
    return json_result["id"]

#creates a playlist "OSU playlist" and returns it's id for use when adding tracks to this playlist
def create_playlist(token,userid,playlist_name,description):
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

    if "error" in json_result:
        raise KeyError
    
    return json_result["id"]

#adds tracks into the playlist
def add_songs(token, id, tracks):
    
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

    if "error" in json_result:
        raise KeyError

    return json.dumps(json_result)

def search_artist(name, token):

    query = urllib.parse.quote(name)
    url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1&offset=0"
    headers = {"Authorization": "Bearer " + token}

    result = get(url, headers=headers)
    json_result = json.loads(result.content)

    if "error" in json_result:
        raise KeyError

    if not json_result["tracks"]["items"]:

        #Reformatting the names from: "artist:Artist Name track:Track Name" to: "Artist Name Track Name"
        artist, track = name.split("track:")
        artist = artist.removeprefix("artist:")
        message = artist + track

        return "Error" + message
    else:
        return json_result["tracks"]["items"][0]["uri"]

def get_user_id(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result["id"]

if __name__ == "__main__":

    try:
        get_user_id("name")
    except KeyError:
        print("error")

