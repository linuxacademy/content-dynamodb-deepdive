#!/usr/bin/env python3

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

config = Config(retries=dict(max_attempts=1))

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


def put_item():
    """Produce a ProvisionedThroughputExceededException"""
    try:
        print("Put item")
        table.put_item(Item={"Artist": "Foo", "SongTitle": "Bar"})
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')


def get_item():
    """Produce a ProvisionedThroughputExceededException"""
    try:
        print("Get item")
        table.get_item(Key={"Artist": "Foo", "SongTitle": "Bar"})
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')


def user_error():
    """Produce a ValidationException"""
    try:
        table.put_item(Item={"BadKey": "BadValue"})
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')


def main():
    create_table()

    while True:
        put_item()
        get_item()
        user_error()


if __name__ == "__main__":
    main()
