#!/usr/bin/env python3

"""
Create a Scores table and Award GSI
"""

import boto3

client = boto3.client("dynamodb")
table_name = "game"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)

response = client.create_table(
    TableName=table_name,
    KeySchema=[
        {"AttributeName": "game", "KeyType": "HASH"},
        {"AttributeName": "user", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "game", "AttributeType": "S"},
        {"AttributeName": "user", "AttributeType": "S"},
        {"AttributeName": "award", "AttributeType": "S"},
    ],
    GlobalSecondaryIndexes=[
        {
            "IndexName": "award-index",
            "KeySchema": [{"AttributeName": "award", "KeyType": "HASH"}],
            "Projection": {"ProjectionType": "INCLUDE", "NonKeyAttributes": ["score"]},
        }
    ],
    BillingMode="PAY_PER_REQUEST",
)
print(response)

print(f"Waiting for table {table_name}...")
waiter = client.get_waiter("table_exists")
waiter.wait(TableName=table_name)
response = client.describe_table(TableName=table_name)
print(response["Table"]["TableStatus"])

items = [
    {"game": "Game 1", "user": "Mark", "score": 12, "date": "2019-07-12"},
    {
        "game": "Game 1",
        "user": "Kelby",
        "score": 23,
        "date": "2019-07-12",
        "award": "champ",
    },
    {"game": "Game 2", "user": "John", "score": 27, "date": "2019-07-12"},
    {
        "game": "Game 2",
        "user": "Julie",
        "score": 42,
        "date": "2019-07-12",
        "award": "champ",
    },
    {
        "game": "Game 3",
        "user": "Terry",
        "score": 36,
        "date": "2019-07-12",
        "award": "champ",
    },
    {"game": "Game 3", "user": "Moosa", "score": 32, "date": "2019-07-12"},
]

[table.put_item(Item=i) for i in items]
