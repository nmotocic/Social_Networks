from models.artist import Artist
from dataclasses import dataclass
from typing import List

@dataclass
class Song:
    id : int
    name : str
    url : str
    artist : Artist
    tags : List
 
