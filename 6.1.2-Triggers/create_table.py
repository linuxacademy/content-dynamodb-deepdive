#!/usr/bin/env python3

import boto3

dynamodb = boto3.resource("dynamodb")
client = boto3.client("dynamodb")
table_name = "orders"
table = dynamodb.Table(table_name)
existing_tables = client.list_tables()["TableNames"]

if table_name not in existing_tables:
    print(f"Creating {table_name} table")
    response = client.create_table(
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
