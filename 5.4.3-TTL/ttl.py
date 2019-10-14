#!/usr/bin/env python3

import os
import time
import uuid

import boto3
from botocore.exceptions import ClientError

client = boto3.client("dynamodb")

existing_tables = client.list_tables()["TableNames"]

table_name = "session_data"

if table_name not in existing_tables:
    print(f"Creating {table_name} table")
    response = client.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},
            {"AttributeName": "ttl", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "ttl", "AttributeType": "N"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"Waiting for table session_data...")
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=table_name)

# Write dummy session data

for _ in range(10):
    try:
        expiry = int(time.time() + 3600 * 24 * 7)  # one week
        response = client.put_item(
            TableName=table_name,
            Item={
                "id": {"S": str(uuid.uuid4())},
                "ttl": {"N": str(expiry)},
                "data": {"B": os.urandom(1024)},
            },
        )
    except ClientError as e:
        print(e)
    else:
        print("PutItem succeeded:")
        print(response)

# Query session data, filtering out TTL (return unexpired items)

try:
    current_epoch = int(time.time())
    response = client.scan(
        TableName=table_name,
        FilterExpression="#t > :ttl",
        ExpressionAttributeNames={"#t": "ttl"},
        ExpressionAttributeValues={":ttl": {"N": str(current_epoch)}},
    )
except ClientError as e:
    print(e)
else:
    if "Items" in response:
        for item in response["Items"]:
            print(f"{item['id']} {item['ttl']}")
