import json

from boto3.dynamodb.conditions import Key, Attr

from webapp.models import pinehead_table, replace_decimals
from webapp.models.artist import get_artist_by_id
from webapp.models.models import Album, Artist, Track


def album_from_item(item):
    album = Album(
        item["id"],
        item.get("sku", ""),
        item.get("artist_id", 0),
        item["name_title"],
        item.get("year", 0),
        item.get("format", ""),
        item.get("price", 0.0),
    )

    if "cover_art" in item:
        album.cover_art = item["cover_art"].value

    # album.artist = get_artist_by_id(album.artist_id)

    return album


def get_all_albums(prev_evaluated_key=None, last_evaluated_key=None, per_page=9):

    if last_evaluated_key is None:
        response = pinehead_table.scan(Limit=per_page)
    else:
        prev_evaluated_key = last_evaluated_key
        last_evaluated_key = json.loads(last_evaluated_key)
        response = pinehead_table.scan(
            Limit=per_page, ExclusiveStartKey=last_evaluated_key
        )

    if "LastEvaluatedKey" in response:
        last_evaluated_key = response["LastEvaluatedKey"]

    last_evaluated_key = replace_decimals(last_evaluated_key)
    last_evaluated_key_json = json.dumps(last_evaluated_key)

    albums = []

    for item in response["Items"]:
        album = album_from_item(item)
        album.artist = get_artist_by_id(album.artist_id)
        albums.append(album)

    return albums, last_evaluated_key_json, prev_evaluated_key


def get_album_by_id(album_id):
    response = pinehead_table.query(
        KeyConditionExpression=Key("type").eq("album") & Key("id").eq(album_id),
    )

    if len(response["Items"]) == 0:
        return None

    return album_from_item(response["Items"][0])


def get_albums_by_artist_name(artist_name):
    # TODO
    albums = []
    return albums


def find_albums_by_artist_name(artist_name):
    print("Finding albums by artist name:", artist_name)

    # Step 1 - Get artist_id by artist name

    # Uses LSI artist_name-title-index
    response = pinehead_table.query(
        IndexName="name_title-index",
        KeyConditionExpression=Key("name_title").eq(artist_name),
        FilterExpression=Attr("type").eq("artist"),
    )

    artist_id = response["Items"][0]["id"]

    # Step 2 - Get albums by artist_id

    albums = find_albums_by_artist_id(artist_id)

    return albums


def find_album_by_artist_and_title(artist_name, title):
    print(f"Finding albums with artist={artist_name} and title={title}")

    # Uses LSI artist_name-title-index
    response = pinehead_table.query(
        IndexName="artist_name-title-index",
        KeyConditionExpression=Key("artist_name").eq(artist_name),
        FilterExpression=Attr("title").eq(title),
    )

    data = response["Items"]

    albums = []

    for item in data:
        album = album_from_item(item)

        print(json.dumps(item))

        if "cover_art" in item:
            album.cover_art = item["cover_art"].value

        albums.append(album)

    return albums


def find_albums_by_title(album_title):
    print("Finding albums with title:", album_title)
    fe = Attr("type").eq("album")
    response = pinehead_table.query(
        IndexName="name_title-index",
        KeyConditionExpression=Key("name_title").eq(album_title),
        FilterExpression=fe,
    )
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = pinehead_table.query(
            IndexName="name_title-index",
            KeyConditionExpression=Key("name_title").eq(album_title),
            FilterExpression=fe,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        data.extend(response["Items"])

    albums = []

    for item in data:
        album = album_from_item(item)
        album.artist = get_artist_by_id(album.artist_id)
        albums.append(album)

    return albums


def find_albums_by_track(track_name):
    print("Finding tracks named:", track_name)
    fe = Attr("type").eq("track")
    response = pinehead_table.query(
        IndexName="name_title-index",
        KeyConditionExpression=Key("name_title").eq(track_name),
        FilterExpression=fe,
    )
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = pinehead_table.query(
            IndexName="name_title-index",
            KeyConditionExpression=Key("name_title").eq(track_name),
            FilterExpression=fe,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        data.extend(response["Items"])

    albums = []

    for item in data:
        album = get_album_by_id(item["album_id"])
        album.artist = get_artist_by_id(album.artist_id)
        albums.append(album)

    return albums


def find_albums_by_artist_id(artist_id):

    print("Finding albums where artist_id =", artist_id)

    response = pinehead_table.query(
        IndexName="artist_id-type-index",
        KeyConditionExpression=Key("artist_id").eq(artist_id) & Key("type").eq("album"),
    )

    albums = []

    for item in response["Items"]:
        album = album_from_item(item)
        albums.append(album)

    # print(albums)

    return albums

