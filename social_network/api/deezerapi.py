import requests
import json
import sys
sys.path.append("social_network")
from models import Song, Artist
from pathlib import Path
import csv

_here = Path(__file__).parent

url = "https://deezerdevs-deezer.p.rapidapi.com/playlist/1253264921"

headers = {
    'x-rapidapi-key': "368d45b3damshabc88bb83fcaf04p1b3bccjsnaba53e042f8d",
    'x-rapidapi-host': "deezerdevs-deezer.p.rapidapi.com"
    }

response = requests.request("GET", url, headers=headers)

output_json  = response.json()

track_list = output_json["tracks"]["data"]

song_list = []
artist_list = []
for i in range(len(track_list)):
    artist = Artist(id = track_list[i]['artist']['id'],
                    name = track_list[i]['artist']['name'])
    song = Song(id = track_list[i]['id'],
                name = track_list[i]['title'],
                url = track_list[i]['link'],
                artist = artist)
    artist_list.append(artist)
    song_list.append(song)
    
'''
song_path = _here.parent.joinpath("snapshots/deezer_songs.csv")
with open(song_path, 'w', newline='') as f:
    fieldnames = ['id','name', "url"]
    writer = csv.DictWriter(f, delimiter = ',', fieldnames=fieldnames)
    writer.writeheader()
    for song in song_list:
        writer.writerow({"id":song.id,
                         "name":song.name,
                         "url":song.url})
    print("success")

artist_path = _here.parent.joinpath("snapshots/deezer_artists.csv")  
with open(artist_path, 'w', newline='') as f:
    header = ["id", "name"]
    writer = csv.DictWriter(f, delimiter = ',', fieldnames=header)
    writer.writeheader()
    for artist in artist_list:
        writer.writerow({"id":artist.id,
                         "name":artist.name,
                         })
    print("success")
'''

data_path = _here.parent.joinpath("snapshots/deezer_data.csv")
with open(data_path, 'w', newline='') as f:
    fieldnames = ['id','name', "url", "artist_id", "artist_name"]
    writer = csv.DictWriter(f, delimiter = ',', fieldnames=fieldnames)
    writer.writeheader()
    for song in song_list:
        writer.writerow({"id":song.id,
                         "name":song.name,
                         "url":song.url,
                         "artist_id":song.artist.id,
                         "artist_name":song.artist.name})
    print("success")
