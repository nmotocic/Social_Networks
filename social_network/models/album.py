from models.artist import Artist
from dataclasses import dataclass
from typing import List

@dataclass
class Album:
    id : int
    name : str
    artist : Artist
