import requests
import json
import random
import sys
sys.path.append("social_network")
from models import Song, Artist
from pathlib import Path
import csv

_here = Path(__file__).parent

url = "https://unogsng.p.rapidapi.com/title"

querystring = {"netflixid":"81043135"}

headers = {
    'x-rapidapi-key': "368d45b3damshabc88bb83fcaf04p1b3bccjsnaba53e042f8d",
    'x-rapidapi-host': "unogsng.p.rapidapi.com"
    }
    
response = requests.request("GET", url, headers=headers, params=querystring)

output_json = response.json()
print(output_json)
'''
track_list = output_json["tracks"]

song_list = []
artist_list = []
for i in range(len(track_list)):
    randomId = random.randint(0,100000000)
    artist = Artist(id = randomId,
                    name = track_list[i]['subtitle'])
    song = Song(id = track_list[i]['key'],
                name = track_list[i]['title'],
                url = track_list[i]['url'],
                artist = artist)
    song_list.append(song)
    if artist not in artist_list:
        artist_list.append(artist)


song_path = _here.parent.joinpath("snapshots/shazam_songs.csv")
with open(song_path, 'w', newline='') as f:
    fieldnames = ['id','name', "url"]
    writer = csv.DictWriter(f, delimiter = ',', fieldnames=fieldnames)
    writer.writeheader()
    for song in song_list:
        writer.writerow({"id":song.id,
                         "name":song.name,
                         "url":song.url})
    print("success")

artist_path = _here.parent.joinpath("snapshots/shazam_artists.csv")  
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