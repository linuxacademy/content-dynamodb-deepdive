#!/usr/bin/env python3

from datetime import datetime

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Disable exponential backoff
config = Config(retries=dict(max_attempts=1))
dynamodb = boto3.resource("dynamodb", config=config)
table = dynamodb.Table("album")


def get_item():
    try:
        print(f"[{datetime.strftime(datetime.now(),'%H:%M:%S,%f')}] Get item")
        table.get_item(Key={"id": 29})
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')


def main():
    print(f"Table: {table.name}")
    print(f"ReadCapacityUnits: {table.provisioned_throughput['ReadCapacityUnits']}")
    print(f"WriteCapacityUnits: {table.provisioned_throughput['WriteCapacityUnits']}")

    while True:
        get_item()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        exit(0)
