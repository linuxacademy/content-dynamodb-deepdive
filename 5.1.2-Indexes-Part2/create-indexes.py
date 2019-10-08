#!/usr/bin/env python3

"""
The following queries from our application inform our indexes:
- Album.get_by_artist_id(artist_id)
- Album.find_by_artist(artist_name)
- Album.find_by_artist_ids(artist_ids)
- Album.find_by_title()
- Album.find_by_track()
- Artist.find_by_name()
- Track.get_by_album_id()
"""

from time import sleep

import boto3
from botocore.exceptions import ClientError

client = boto3.client("dynamodb")


def wait_index(table_name):
    """We can only add one index per table at a time"""
    print(f"Waiting for index on {table_name} to be created...")
    index_creating = True

    try:
        while index_creating:
            index_statuses = []
            gsis = client.describe_table(TableName=table_name)["Table"][
                "GlobalSecondaryIndexes"
            ]
            for gsi in gsis:
                index_statuses.append(gsi["IndexStatus"])

            if "CREATING" in index_statuses or "UPDATING" in index_statuses:
                sleep(3)
            else:
                index_creating = False
    except KeyError:
        pass


print("Adding GSIs to artist table")

try:
    response = client.update_table(
        TableName="artist",
        AttributeDefinitions=[{"AttributeName": "name", "AttributeType": "S"}],
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    "IndexName": "name-index",
                    "KeySchema": [{"AttributeName": "name", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            }
        ],
    )
    print(response)
    wait_index("artist")
except ClientError as e:
    if "create an index which already exists" in e.response["Error"]["Message"]:
        print("Index name-index already exists")

print("Adding GSIs to album table")

try:
    response = client.update_table(
        TableName="album",
        AttributeDefinitions=[{"AttributeName": "artist_id", "AttributeType": "N"}],
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    "IndexName": "artist_id-index",
                    "KeySchema": [{"AttributeName": "artist_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            }
        ],
    )
    print(response)
    wait_index("album")
except ClientError as e:
    if "create an index which already exists" in e.response["Error"]["Message"]:
        print("Index artist_id-index already exists")
    else:
        raise e


try:
    response = client.update_table(
        TableName="album",
        AttributeDefinitions=[{"AttributeName": "artist_name", "AttributeType": "S"}],
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    "IndexName": "artist_name-index",
                    "KeySchema": [{"AttributeName": "artist_name", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            }
        ],
    )
    print(response)
    wait_index("album")
except ClientError as e:
    if "create an index which already exists" in e.response["Error"]["Message"]:
        print("Index artist_name-index already exists")
    else:
        raise e

try:
    response = client.update_table(
        TableName="album",
        AttributeDefinitions=[{"AttributeName": "artist_title", "AttributeType": "S"}],
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    "IndexName": "artist_title-index",
                    "KeySchema": [{"AttributeName": "artist_title", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            }
        ],
    )
    print(response)
    wait_index("album")
except ClientError as e:
    if "create an index which already exists" in e.response["Error"]["Message"]:
        print("Index artist_title-index already exists")
    else:
        raise e

print("Adding GSIs to track table")

try:
    response = client.update_table(
        TableName="track",
        AttributeDefinitions=[{"AttributeName": "album_id", "AttributeType": "N"}],
        GlobalSecondaryIndexUpdates=[
            {
                "Create": {
                    "IndexName": "album_id-index",
                    "KeySchema": [{"AttributeName": "album_id", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            }
        ],
    )
    print(response)
    wait_index("track")
except ClientError as e:
    if "create an index which already exists" in e.response["Error"]["Message"]:
        print("Index album_id-index already exists")
    elif "Index is being created" in e.response["Error"]["Message"]:
        print("Index album_id-index is being created")
    else:
        raise e
