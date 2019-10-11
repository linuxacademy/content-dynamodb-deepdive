#!/usr/bin/env python3

import uuid

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

client = boto3.client("dynamodb")

existing_tables = client.list_tables()["TableNames"]

if "orders" not in existing_tables:
    print("Creating orders table")
    response = client.create_table(
        TableName="orders",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"Waiting for table orders...")
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName="orders")

try:
    print("TransactWriteItems")
    response = client.transact_write_items(
        TransactItems=[
            {
                "Update": {
                    "TableName": "album",
                    "Key": {"id": {"N": "28222"}},
                    "UpdateExpression": "set in_stock = in_stock - :val",
                    "ConditionExpression": "in_stock > :in_stock",
                    "ExpressionAttributeValues": {
                        ":val": {"N": "1"},
                        ":in_stock": {"N": "0"},
                    },
                }
            },
            {
                "Put": {
                    "TableName": "orders",
                    "Item": {
                        "id": {"S": str(uuid.uuid4())},
                        "amount": {"N": str(5.5)},
                        "email": {"S": "mark@linuxacademy.com"},
                    },
                }
            },
        ]
    )
except ClientError as e:
    print(e)
else:
    print("TransactWriteItems succeeded:")
    print(response)
