import decimal
import os

import boto3
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

print("INFO: Loading function")

BUCKET = os.environ["BUCKET"]

table = boto3.resource("dynamodb").Table("orders_leaderboard")
s3 = boto3.resource("s3")
td = TypeDeserializer()


def lambda_handler(event, context):
    try:
        for record in event["Records"]:
            data = record["dynamodb"].get("NewImage")
            d = {}
            for key in data:
                d[key] = td.deserialize(data[key])

            title = d["album"]["title"]
            artist = d["album"]["artist_name"]
            update_leaderboard(title, artist)

            print("INFO: orders_leaderboard updated")

        print("INFO: Uploading data to S3")
        upload_index()
    except ClientError as e:
        print(f'ERROR: {e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
        raise


def update_leaderboard(album_title, artist_name):
    try:
        print(f"INFO: Updating order totals for '{album_title}' by '{artist_name}'")
        table.update_item(
            Key={"album": album_title, "artist": artist_name},
            UpdateExpression="SET order_count = order_count + :val",
            ExpressionAttributeValues={":val": decimal.Decimal(1)},
        )
    except ClientError:
        print("WARN: Seeding order_count")
        try:
            table.put_item(
                Item={
                    "album": album_title,
                    "artist": artist_name,
                    "order_count": decimal.Decimal(1),
                }
            )
        except ClientError as e:
            print(
                f'ERROR: {e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}'
            )
            raise


def upload_index():
    try:
        html_head = """
            <html>
                <head>
                    <style>
                    table, th, td {
                    border: 1px solid black;
                    }
                    </style>
                </head>
                <body>
                <h1>Pinehead Records: Top Orders</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Album</th>
                            <th>Artist</th>
                            <th># Sold</th>
                        </tr>
                    </thead>
                    <tbody>
                """
        table_body = ""

        html_foot = "</tbody></table></body></html>"

        print(f"INFO: Scanning order_leaderboard table")
        items = table.scan()["Items"]
        items.sort(key=lambda x: x["order_count"], reverse=True)

        for item in items:
            table_body += (
                "<tr>"
                + "<td>"
                + item["album"]
                + "</td> "
                + "<td>"
                + item["artist"]
                + "</td> "
                + "<td>"
                + str(item["order_count"])
                + "</td> "
                + "</tr>"
            )

        print(f"INFO: Generating index.html")
        html = html_head + table_body + html_foot

        print(f"INFO: Uploading to S3 bucket")
        s3.Bucket(BUCKET).put_object(
            Key="index.html", Body=html.encode("utf-8"), ContentType="text/html"
        )

    except ClientError as e:
        print(f'ERROR: {e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
        raise
