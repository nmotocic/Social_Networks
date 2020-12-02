import sys
sys.path.append("social_network")
import csv
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile

_here = Path(__file__).parent

filename = "lastfm_data.csv"
tempfile = NamedTemporaryFile(mode='w', delete=False)

artist_dict = dict()

data_path = _here.parent.joinpath("snapshots/lastfm_data.csv")
with open(data_path, 'r', newline='') as f, tempfile:
    fieldnames = ['id','name', "url","tags", "artist_id", "artist_name"]
    reader = csv.DictReader(f, delimiter = ',')
    writer = csv.DictWriter(tempfile, delimiter = ",", fieldnames = fieldnames)
    for row in reader:
        artist = row["artist_name"]
        if artist not in artist_dict.keys():
            artist_dict[artist] = row["artist_id"]
            row["artist_id"] = artist_dict[artist]
    
    for row in reader:
        for artist_dict in artist_dict.keys():
            if artist == row["artist_name"]:
                row["artist_id"] = artist_dict[artist]
                print(row)
        writer.writerow(row)
    print("success")

shutil.move(tempfile.name, filename)

print(artist_dict)