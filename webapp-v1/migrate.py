#!/usr/bin/env python3

"""
This is a naïve "v0" implementation, which creates 3 DynamoDB tables - one for
each MySQL table. Each MySQL table is imported into DDB using multiprocessing
and the DynamoDB batch writer for performance.
"""

from base64 import b64encode
import decimal
from multiprocessing import Pool, Process, cpu_count

import boto3
import pymysql.cursors

dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:8000/")
ddb_artist = dynamodb.Table("artist")
ddb_album = dynamodb.Table("album")
ddb_track = dynamodb.Table("track")


def import_artist():

    offsets = get_offsets("artist")
    tuples = [("artist", offset) for offset in offsets]

    pool = Pool(cpu_count())
    results = pool.map(process_artist, tuples)
    pool.close()
    pool.join()
    print(results)


def import_album():

    offsets = get_offsets("album")
    tuples = [("album", offset) for offset in offsets]

    pool = Pool(cpu_count())
    results = pool.map(process_album, tuples)
    pool.close()
    pool.join()
    print(results)


def import_track():

    offsets = get_offsets("track")
    tuples = [("track", offset) for offset in offsets]

    pool = Pool(cpu_count())
    results = pool.map(process_track, tuples)
    pool.close()
    pool.join()
    print(results)


def process_artist(info):
    table_name, offset = info
    con = get_connection()

    with con.cursor() as cursor:
        sql = f"SELECT id, name from {table_name} LIMIT {offset}, 1000"
        print(sql)
        cursor.execute(sql)
        for row in cursor.fetchall():
            with ddb_artist.batch_writer() as batch:
                batch.put_item(Item={"id": row["id"], "name": row["name"]})

    con.close()


def process_album(info):
    table_name, offset = info
    con = get_connection()

    with con.cursor() as cursor:
        sql = f"SELECT * from {table_name} LIMIT {offset}, 1000"
        print(sql)
        cursor.execute(sql)
        for row in cursor.fetchall():

            item = {
                "id": row["id"],
                "sku": row["sku"],
                "artist_id": row["artist_id"],
                "title": row["title"],
                "year": row["year"],
                "format": row["format"],
                "price": decimal.Decimal(row["price"]),
            }

            if row["cover_art"] != b"":
                cover_art = b64encode(row["cover_art"])
                item["cover_art"] = cover_art

            with ddb_album.batch_writer() as batch:
                batch.put_item(Item=item)

    con.close()


def process_track(info):
    table_name, offset = info
    con = get_connection()

    with con.cursor() as cursor:
        sql = f"SELECT * from {table_name} LIMIT {offset}, 1000"
        print(sql)
        cursor.execute(sql)
        for row in cursor.fetchall():
            with ddb_track.batch_writer() as batch:
                batch.put_item(
                    Item={
                        "id": row["id"],
                        "album_id": row["album_id"],
                        "name": row["name"],
                        "length": row["length"],
                        "number": row["number"],
                    }
                )

    con.close()


def get_connection():
    con = pymysql.connect(
        host="localhost",
        user="pinehead",
        password="pinehead",
        db="pinehead",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return con


def get_offsets(table_name: str, buckets: int = 1000):
    con = get_connection()
    with con.cursor() as cursor:
        sql = f"SELECT count(id) from {table_name}"
        cursor.execute(sql)
        row = cursor.fetchone()
        row_count = row["count(id)"]
    con.close()
    offsets = list(range(0, row_count, buckets))
    return offsets


if __name__ == "__main__":
    artist_proc = Process(target=import_artist)
    album_proc = Process(target=import_album)
    track_proc = Process(target=import_track)
    artist_proc.start()
    album_proc.start()
    track_proc.start()
    artist_proc.join()
    album_proc.join()
    track_proc.join()
