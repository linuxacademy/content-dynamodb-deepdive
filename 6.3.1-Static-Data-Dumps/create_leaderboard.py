#!/usr/bin/env python3

import boto3

table_name = "orders_leaderboard"
client = boto3.client("dynamodb")

print(f"Creating {table_name} table")
response = client.create_table(
    TableName=table_name,
    KeySchema=[
        {"AttributeName": "album", "KeyType": "HASH"},
        {"AttributeName": "artist", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "album", "AttributeType": "S"},
        {"AttributeName": "artist", "AttributeType": "S"},
        # {"AttributeName": "order_count", "AttributeType": "N"},
    ],
    # LocalSecondaryIndexes=[
    #     {
    #         "IndexName": "order_count-index",
    #         "KeySchema": [
    #             {"AttributeName": "album", "KeyType": "HASH"},
    #             {"AttributeName": "order_count", "KeyType": "RANGE"},
    #         ],
    #         "Projection": {"ProjectionType": "ALL"},
    #     }
    # ],
    BillingMode="PAY_PER_REQUEST",
)
print(response)

print(f"Waiting for table {table_name}...")
waiter = client.get_waiter("table_exists")
waiter.wait(TableName=table_name)
response = client.describe_table(TableName=table_name)
print(response["Table"]["TableStatus"])
