from __future__ import annotations

import decimal
import json
import os
from typing import List

import boto3
from boto3.dynamodb.conditions import Attr, Key
from flask import abort
from flask_login import UserMixin

from webapp import app, login_manager


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def replace_decimals(obj):
    """ Because the Boto3 DynamoDB client turns all numeric types into Decimals
    (which is actually the right thing to do) we need to convert those
    Decimal values back into integers or floats before serializing to JSON.
    """
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


# boto3.set_stream_logger(name='botocore')  # enables boto3 debug logging

IS_OFFLINE = os.environ.get("IS_OFFLINE")

if IS_OFFLINE:
    dynamodb = boto3.client("dynamodb", endpoint_url="http://localhost:8000")
else:
    dynamodb = boto3.client("dynamodb")

artist_table = boto3.resource("dynamodb").Table("artist")
album_table = boto3.resource("dynamodb").Table("album")
track_table = boto3.resource("dynamodb").Table("track")
user_table = boto3.resource("dynamodb").Table("user")


class User(UserMixin):
    """Standard flask_login UserMixin"""

    pass


class Track:
    def __init__(self, id, album_id, name, length, number):
        self._id = id
        self._album_id = album_id
        self._name = name
        self._length = length
        self._number = number

    @property
    def id(self):
        return self._id

    @property
    def album_id(self):
        return self._album_id

    @property
    def name(self):
        return self._name

    @property
    def length(self):
        return self._length

    @property
    def length_str(self) -> str:
        try:
            s = self.length / 1000
            m, s = divmod(s, 60)
            return f"{m:.0f}:{s:02.0f}"
        except TypeError:
            return "(track length unavailable)"

    @property
    def number(self):
        return self._number

    @staticmethod
    def get_track(track_id):
        resp = dynamodb.get_item(TableName="track", Key={"id": {"N": track_id}})
        item = resp.get("Item")
        track = Track(
            item["id"], item["album_id"], item["name"], item["length"], item["number"]
        )
        return track

    @staticmethod
    def get_by_album_id(album_id: int):

        response = track_table.scan(FilterExpression=Attr("album_id").eq(album_id))

        tracks = []

        for item in response["Items"]:
            track = Track(
                item["id"],
                item["album_id"],
                item["name"],
                item["length"],
                item["number"],
            )

            tracks.append(track)

        return tracks

    def __repr__(self):
        return f"Track('{self.name}')"


class Album:
    def __init__(
        self,
        id,
        sku,
        artist_id,
        title,
        year,
        format,
        price,
        cover_art=None,
        tracks: List[Track] = [],
    ):
        self._id = id
        self._sku = sku
        self._artist_id = artist_id
        self._artist = None
        self._title = title
        self._year = year
        self._format = format
        self._price = price
        self._cover_art = cover_art
        self._tracks = tracks

    @property
    def id(self):
        return self._id

    @property
    def sku(self):
        return self._sku

    @property
    def artist_id(self):
        return self._artist_id

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def format(self):
        return self._format

    @property
    def price(self):
        return self._price

    @property
    def artist(self) -> Artist:
        return self._artist

    @artist.setter
    def artist(self, value: Artist):
        self._artist = value

    @property
    def tracks(self) -> List[Track]:
        return self._tracks

    @tracks.setter
    def tracks(self, value: List[Track]):
        self._tracks = value

    @property
    def album_art(self):
        id_album = list(str(self.id))
        id_album.reverse()
        filepath = "/".join(id_album)
        s3_uri = f"{app.config['S3_PREFIX']}albumart/{filepath}/{self.id}.jpg"
        print(s3_uri)
        return s3_uri

    @staticmethod
    def get_by_id(album_id: int):

        print("Get album by id:", album_id)

        response = album_table.query(KeyConditionExpression=Key("id").eq(album_id))

        if response["Count"] == 0:
            return None

        item = response["Items"][0]

        album = Album(
            int(item["id"]),
            item["sku"],
            int(item["artist_id"]),
            item["title"],
            int(item["year"]),
            item["format"],
            item["price"],
        )

        if "cover_art" in item:
            album.cover_art = item["cover_art"].value

        print(album)

        print("Getting tracks for album id:", album_id)

        album.artist = Artist.get_by_id(album.artist_id, ignore_albums=True)

        album.tracks = Track.get_by_album_id(album_id)  # test album_id=472134

        return album

    @staticmethod
    def get_all(prev_evaluated_key=None, last_evaluated_key=None, per_page=9):

        if last_evaluated_key is None:
            response = album_table.scan(Limit=per_page)
        else:
            prev_evaluated_key = last_evaluated_key
            last_evaluated_key = json.loads(last_evaluated_key)
            response = album_table.scan(
                Limit=per_page, ExclusiveStartKey=last_evaluated_key
            )

        if "LastEvaluatedKey" in response:
            last_evaluated_key = response["LastEvaluatedKey"]

        last_evaluated_key = replace_decimals(last_evaluated_key)
        last_evaluated_key_json = json.dumps(last_evaluated_key)

        albums = []

        for item in response["Items"]:
            album = Album(
                item["id"],
                item["sku"],
                item["artist_id"],
                item["title"],
                item["year"],
                item["format"],
                item["price"],
                cover_art=b"",
                tracks=[],
            )

            album.artist = Artist.get_by_id(album.artist_id, ignore_albums=True)

            albums.append(album)

        return albums, last_evaluated_key_json, prev_evaluated_key

    @staticmethod
    def get_by_artist_id(artist_id: int):

        print("Getting albums for artist id:", artist_id)

        fe = Attr("artist_id").eq(artist_id)

        response = album_table.scan(FilterExpression=fe)

        data = []

        while "LastEvaluatedKey" in response:
            response = album_table.scan(
                FilterExpression=fe, ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])

        albums = []

        for item in data:
            album = Album(
                int(item["id"]),
                item["sku"],
                int(item["artist_id"]),
                item["title"],
                int(item["year"]),
                item["format"],
                item["price"],
            )

            albums.append(album)

        albums.sort(key=lambda x: x.year, reverse=True)

        return albums

    @staticmethod
    def find_by_artist(artist_name, prev, last, per_page):

        print("Finding artist by name:", artist_name)

        # get all artist_ids where name = artist_name
        artists = Artist.find_by_name(artist_name)

        artist_ids = [a.id for a in artists]

        if artist_ids == []:
            abort(404)

        # scan albums in artist_ids
        albums, last, prev = Album.find_by_artist_ids(artist_ids, prev, last, per_page)

        return albums, last, prev

    @staticmethod
    def find_by_artist_ids(
        artist_ids: List[int], prev_evaluated_key, last_evaluated_key, per_page=9
    ):

        print("Finding albums where artist_id in:", artist_ids)

        fe = Attr("artist_id").is_in(artist_ids)

        if last_evaluated_key is None:
            response = album_table.scan(FilterExpression=fe, Limit=per_page)
        else:
            prev_evaluated_key = last_evaluated_key
            last_evaluated_key = json.loads(last_evaluated_key)
            response = album_table.scan(
                FilterExpression=fe,
                Limit=per_page,
                ExclusiveStartKey=last_evaluated_key,
            )

        if "LastEvaluatedKey" in response:
            last_evaluated_key = response["LastEvaluatedKey"]

        last_evaluated_key = replace_decimals(last_evaluated_key)
        last_evaluated_key_json = json.dumps(last_evaluated_key)
        data = response["Items"]

        # this can take a while without indexes....~40s

        while "LastEvaluatedKey" in response:
            response = album_table.scan(
                FilterExpression=fe, ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            last_evaluated_key = response["LastEvaluatedKey"]
            last_evaluated_key = replace_decimals(last_evaluated_key)
            last_evaluated_key_json = json.dumps(last_evaluated_key)
            data.extend(response["Items"])

        albums = []

        for item in data:
            album = Album(
                int(item["id"]),
                item["sku"],
                int(item["artist_id"]),
                item["title"],
                int(item["year"]),
                item["format"],
                item["price"],
            )
            print(album)
            albums.append(album)

        return albums, last_evaluated_key_json, prev_evaluated_key

    @staticmethod
    def find_by_title(album_title, prev_evaluated_key, last_evaluated_key, per_page=9):
        print("Finding albums with title:", album_title)

        fe = Attr("title").eq(album_title)

        response = album_table.scan(FilterExpression=fe)

        data = response["Items"]

        # without indexes, this can take a while...~40s

        while "LastEvaluatedKey" in response:
            response = album_table.scan(
                FilterExpression=fe, ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            last_evaluated_key = replace_decimals(last_evaluated_key)
            last_evaluated_key_json = json.dumps(last_evaluated_key)
            data.extend(response["Items"])

        albums = []

        for item in data:
            album = Album(
                int(item["id"]),
                item["sku"],
                int(item["artist_id"]),
                item["title"],
                int(item["year"]),
                item["format"],
                item["price"],
            )
            print(album)
            albums.append(album)

        return albums, last_evaluated_key_json, prev_evaluated_key

    @staticmethod
    def find_by_track(track_name):

        print("Finding tracks named:", track_name)

        fe = Attr("name").eq(track_name)

        response = track_table.scan(FilterExpression=fe)

        data = response["Items"]

        # without indexes, this can take a while...~40s

        while "LastEvaluatedKey" in response:
            response = track_table.scan(
                FilterExpression=fe, ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])
            print(".")

        tracks = []

        for item in data:
            track = Track(
                int(item["id"]),
                int(item["album_id"]),
                item["name"],
                item["length"],
                item["number"],
            )
            tracks.append(track)

        albums = []

        for t in tracks:
            album = Album.get_by_id(t.album_id)
            if album is None:
                continue
            albums.append(album)

        return albums

    def __repr__(self):
        return f"Album('{self._title}')"


class Artist:
    def __init__(self, id, name, albums: List[Album]):
        self._id = id
        self._name = name
        self._albums = []

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def albums(self):
        return self._albums

    @albums.setter
    def albums(self, value):
        self._albums = value

    @staticmethod
    def get_by_id(artist_id, ignore_albums=False):

        print("Getting artist by id:", artist_id)

        response = artist_table.query(KeyConditionExpression=Key("id").eq(artist_id))

        item = response["Items"][0]

        artist = Artist(int(item["id"]), item["name"], albums=[])

        if ignore_albums:
            return artist

        albums = Album.get_by_artist_id(artist_id)

        if albums is not None:
            artist.albums = albums

        return artist

    @staticmethod
    def find_by_name(artist_name):

        print("Finding artist by name:", artist_name)

        fe = Attr("name").eq(artist_name)

        response = artist_table.scan(FilterExpression=fe)

        data = response["Items"]

        # without indexes, this can take a while...~10s

        while "LastEvaluatedKey" in response:
            response = artist_table.scan(
                FilterExpression=fe, ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            data.extend(response["Items"])

        artists = []

        for item in data:
            artist = Artist(int(item["id"]), item["name"], albums=[])
            artists.append(artist)

        return artists

    def __repr__(self):
        return f"Artist('{self.name}')"
