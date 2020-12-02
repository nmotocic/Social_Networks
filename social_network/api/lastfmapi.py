import requests
import json
import random
import sys
sys.path.append("social_network")
from models import Song, Artist
from typing import List
from pathlib import Path
import csv

_here = Path(__file__).parent

API_KEY = '7c2a3bd50ed894693b82222194f84366'
USER_AGENT = 'systematic_32'

def lastfm_get(payload):
    headers = { 'user-agent' : USER_AGENT}
    url = 'http://ws.audioscrobbler.com/2.0/'
    #Add API key and format to the payload
    payload['api_key'] = API_KEY
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response

def getTags(song_name, artist_name):
    tags = []
    track_info = lastfm_get({"method" : "track.getInfo" , "track" : song_name, "artist" : artist_name})
    output = track_info.json()
    toptag_list = output["track"]["toptags"]["tag"]
    for tag in toptag_list:
        tags.append(tag["name"])
    return tags


r = lastfm_get({
    'method' : 'chart.gettoptracks'
})
r.status_code

output_json  = r.json()
track_list = output_json["tracks"]["track"]



song_list = []
artist_list = []
for i in range(len(track_list)):
    randomId = random.randint(0,100000)
    tags = getTags(track_list[i]['name'], track_list[i]['artist']['name'])
    artist = Artist(
                    name = track_list[i]['artist']['name'])
    song = Song(id = randomId,
                name = track_list[i]['name'],
                url = track_list[i]['url'],
                artist = artist,
                tags = tags)
    artist_list.append(artist)
    song_list.append(song)

'''
song_path = _here.parent.joinpath("snapshots/lastfm_songs.csv")
with open(song_path, 'w', newline='') as f:
    fieldnames = ['id','name', "url", "tags"]
    writer = csv.DictWriter(f, delimiter = ',', fieldnames=fieldnames)
    writer.writeheader()
    for song in song_list:
        writer.writerow({"id":song.id,
                         "name":song.name,
                         "url":song.url,
                         "tags" : song.tags})
    print("success")

artist_path = _here.parent.joinpath("snapshots/lastfm_artists.csv")  
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

data_path = _here.parent.joinpath("snapshots/lastfm_data.csv")
with open(data_path, 'w', newline='') as f:
    fieldnames = ['id','name', "url","tags", "artist_name"]
    writer = csv.DictWriter(f, delimiter = ',', fieldnames=fieldnames)
    writer.writeheader()
    for song in song_list:
        writer.writerow({"id":song.id,
                         "name":song.name,
                         "url":song.url,
                         "tags" : song.tags,
                         "artist_name":song.artist.name})
    print("success")
