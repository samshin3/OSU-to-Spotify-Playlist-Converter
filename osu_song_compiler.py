import os

def compile_songs(path):

    songs = os.listdir(path) #Get's the full list of names of folders in the path
    song_list = []

            #Splits the folder name into the artist and track title, removes the map code
    for file_name in songs: 
        separated = file_name.split(" ")
        index = separated.index("-")

        artist = str(" ".join(separated[1:index]))
        track = (" ".join(separated[index + 1:]))
        if track.endswith("[no video]"):
             
            track = track.removesuffix("[no video]")

        merge = [artist.replace("'","") + "-" + track.replace("'","")]
        song_list.append(merge)

    unique_songs = dupe_remover(song_list)
    flat_list = [item for sublist in unique_songs for item in sublist]    

    return flat_list

#Function removes duplicate values for songs
def dupe_remover(duplicate):
    list_to_set = {tuple(inner) for inner in duplicate}
    dupe_free_list = [list(t) for t in list_to_set]
    return dupe_free_list


if __name__ == "__main__":
    songs = compile_songs("Songs")

    print(songs)
