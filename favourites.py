from ossapi import Ossapi
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("OSU_CLIENT_ID")
client_secret = os.getenv("OSU_CLIENT_SECRET")
api = Ossapi(client_id,client_secret)

#Searches for Username and returns their id
def check_user(username):
    return api.user(username).id

#Takes the user id and category to decide which songs to look for
def query_maker(user_id,category):

    user = api.user_beatmaps(user_id = str(user_id),type=category, limit=100,offset=None)
    songs_list=[]

#Creates a song list that fits the spotify search engine
    for n in range(len(user)):
        artist = user[n].artist.replace("'","")
        track = user[n].title.replace("'","")

        songs_list.append(f"{artist}-{track}")

    return songs_list

if __name__ == "__main__":

    while True:
    
        cat = input("Which category do you want to search for? ")
        flat_list = query_maker(check_user("Cookchomper"),cat)
        if flat_list:
            break
        else:
            print("No beatmap found in specified category")
    print(flat_list)