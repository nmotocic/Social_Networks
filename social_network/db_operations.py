import csv
import sys
sys.path.append("social_network")
from models import Song, Artist

def clear(db):
    command = "MATCH (node) DETACH DELETE node"
    db.execute_query(command)

def generate_songs(path):
    songs = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            artist = Artist(name = row['artist_name'])
            tags_list = row["tags"][1:-1]
            song = Song(id = row['id'],
                name = row['name'],
                url = row['url'],
                artist = artist,
                tags = tags_list)
            songs.append(song)
    return songs

def generate_artists(path):
    artists = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            artist = row['artist_name']
            if artist not in artists:
                artists.append(artist)
    return artists

def generate_tags(path):
    tags = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            tags_list = row["tags"][1:-1]
            print(tags_list)
            for tag in tags_list:
                if tag not in tags:
                    tags.append(tag)
    return tags
           
def populate_database(db, songs, artists, tags):
    for song in songs:
        command = (f'CREATE (n:Song {{id: {song.id}, name: "{song.name}" }})')
        db.execute_query(command)
    for artist in artists:
        command =  (f'CREATE (n:Artist {{ name:"{artist}" }})')
        db.execute_query(command)
    '''
    for tag in tags:
        command = (f'CREATE (n:Tag {{name: "{tag}" }})' )      
        db.execute_query(command)   
    ''' 

def generate_connections(db, path):
    with path.open() as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            
            artist = Artist(name = row['artist_name'])
            tags_list = row["tags"][1:-1]
            song = Song(id = row['id'],
                name = row['name'],
                url = row['url'],
                artist = artist,
                tags = tags_list)
            '''
            for tag in tags_list:
                command_b = (f'MATCH (s: Song), (t:Tag) WHERE s.name = {song.name} AND t.tag = {tag} CREATE (s)-[r:HAS_TAG]-(t)')
                db.execute_query(command_b)
            '''
            command_a = (f'MATCH (s: Song), (a: Artist) WHERE s.name = "{song.name}" AND a.name = "{artist.name}" CREATE (s)-[r:IS_LISTENED_ON]->(a)' )
            db.execute_query(command_a)

def generate_user(db, user_data):
    command = (f'CREATE (u: User {{id: {user_data["id"]}, \
                                   name: "{user_data["name"]}", \
                                    screen_name : "{user_data["screen_name"]}", \
                                    email: "{user_data["email"]}" }} )')
    db.execute_query(command)
            