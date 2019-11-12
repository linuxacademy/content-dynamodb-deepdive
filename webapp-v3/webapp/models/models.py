from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from flask_login import UserMixin


@dataclass
class Track:
    id: int
    name: str
    length: int
    number: str


@dataclass
class Album:
    id: int
    sku: str
    artist_id: int
    title: str
    year: int
    format: str
    price: float
    cover_art: str = None
    artist: Artist = None
    tracks: List[Track] = field(default_factory=list)

    @property
    def album_art(self):
        id_album = list(str(self.id))
        id_album.reverse()
        filepath = "/".join(id_album)
        s3_uri = f"{os.environ['S3_PREFIX']}albumart/{filepath}/{self.id}.jpg"
        print(s3_uri)
        return s3_uri


@dataclass
class Artist:
    id: int
    name: str
    albums: List[Album]


class User(UserMixin):
    """Standard flask_login UserMixin"""

    pass
