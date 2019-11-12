from boto3.dynamodb.conditions import Attr, Key

from webapp.models import dynamodb, pinehead_table, replace_decimals
from webapp.models.models import Track


def track_from_item(item):
    track = Track(item["id"], item["name_title"], item["length"], item["number"],)
    return track


def get_tracks_by_album_id(album_id):
    print("Getting tracks where album_id =", album_id)

    response = pinehead_table.query(
        IndexName="type-album_id-index",
        KeyConditionExpression=Key("type").eq("track") & Key("album_id").eq(album_id),
    )

    tracks = []

    for item in response["Items"]:
        track = track_from_item(item)
        tracks.append(track)

    return tracks

