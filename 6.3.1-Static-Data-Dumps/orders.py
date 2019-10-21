#!/usr/bin/env python3

import random
import time
import uuid
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError
from faker import Faker

fake = Faker()
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")


def create_table():
    table_name = "orders"
    client = dynamodb.meta.client
    existing_tables = client.list_tables()["TableNames"]

    if table_name not in existing_tables:
        print(f"Creating {table_name} table")
        client.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "timestamp", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "N"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"Waiting for table orders...")
        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=table_name)


def fake_albums():
    """Place a random number of orders for fake albums"""
    # Generate 100 fake albums
    for _ in range(100):
        try:
            # Create between 2 and 19 orders for this fake album
            artist_name = fake.name()
            title = fake.sentence(3).split(".")[0].title()
            year = fake.year()
            for _ in range(random.randint(2, 20)):
                item = {}
                item["id"] = str(uuid.uuid4())
                item["timestamp"] = int(time.time() * 1000)
                item["amount"] = Decimal("6.86")
                item["email"] = fake.email()
                item["album"] = {
                    "artist_name": artist_name,
                    "format": '12" Vinyl',
                    "title": title,
                    "year": year,
                }
                response = table.put_item(Item=item)
                print(item)
        except ClientError as e:
            print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
        else:
            print(response)


def real_album():
    """Place a bunch of orders for a real album (Prince's "Purple Rain")"""
    for _ in range(487):
        try:
            item = {}
            item["id"] = str(uuid.uuid4())
            item["timestamp"] = int(time.time() * 1000)
            item["amount"] = Decimal("26.50")
            item["email"] = fake.email()
            item["album"] = {
                "artist_name": "Prince",
                "format": '12" Vinyl',
                "title": "Purple Rain",
                "year": 1984,
            }
            response = table.put_item(Item=item)
            print(item)
        except ClientError as e:
            print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
        else:
            print(response)


def one_order():
    """Place one order for a real album (handy for testing)"""
    try:
        item = {}
        item["id"] = str(uuid.uuid4())
        item["timestamp"] = int(time.time() * 1000)
        item["amount"] = Decimal("26.50")
        item["email"] = fake.email()
        item["album"] = {
            "artist_name": "Prince",
            "format": '12" Vinyl',
            "title": "Purple Rain",
            "year": 1984,
        }
        response = table.put_item(Item=item)
        print(item)
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
    else:
        print(response)


if __name__ == "__main__":
    # create_table()
    fake_albums()
    real_album()
    # one_order()
