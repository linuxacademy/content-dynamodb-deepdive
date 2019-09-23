#!/usr/bin/env python3

from datetime import datetime

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(retries=dict(max_attempts=10))  # DynamoDB default is 10

dynamodb = boto3.resource("dynamodb", config=config)
dynamodb_client = boto3.client("dynamodb", config=config)
table_name = "MetricTest"
table = dynamodb.Table(table_name)


def create_table():
    """Create the table"""
    existing_tables = dynamodb_client.list_tables()["TableNames"]
    if table_name in existing_tables:
        print(f"Table {table_name} already exists.")
        return

    dynamodb_client.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "Artist", "KeyType": "HASH"},
            {"AttributeName": "SongTitle", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "Artist", "AttributeType": "S"},
            {"AttributeName": "SongTitle", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
    )

    print(f"Waiting for table {table_name}...")
    waiter = dynamodb_client.get_waiter("table_exists")
    waiter.wait(TableName=table_name)
    response = dynamodb_client.describe_table(TableName=table_name)
    print(response["Table"]["TableStatus"])


def get_item():
    """Demonstrate exponential backoff"""
    try:
        print(f"[{datetime.strftime(datetime.now(),'%H:%M:%S,%f')}] Get item")
        table.get_item(Key={"Artist": "Foo", "SongTitle": "Bar"})
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')


def main():
    create_table()

    while True:
        get_item()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        exit(0)
