from boto3.dynamodb.conditions import Attr, Key

from webapp.models import pinehead_table
from webapp.models.models import Artist


def artist_from_item(item):
    artist = Artist(int(item["id"]), item["name_title"], albums=[])
    return artist


def get_artist_by_id(artist_id):
    print("Getting artist by id:", artist_id)

    response = pinehead_table.query(
        KeyConditionExpression=Key("id").eq(artist_id) & Key("type").eq("artist")
    )

    item = response["Items"][0]
    artist = artist_from_item(item)
    return artist


# def find_artist_by_name(artist_name):
#     print("Finding artist by name:", artist_name)

#     fe = Attr("name").eq(artist_name)

#     response = pinehead_table.scan(FilterExpression=fe)

#     data = response["Items"]

#     # without indexes, this can take a while...~10s

#     while "LastEvaluatedKey" in response:
#         response = pinehead_table.scan(
#             FilterExpression=fe, ExclusiveStartKey=response["LastEvaluatedKey"]
#         )
#         data.extend(response["Items"])

#     artists = []

#     for item in data:
#         artist = Artist(int(item["id"]), item["name"], albums=[])
#         artists.append(artist)

#     return artists
