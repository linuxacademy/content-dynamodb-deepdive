#!/usr/bin/env python3

import time
import uuid
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("orders")

try:
    item = {}
    item["id"] = str(uuid.uuid4())
    item["timestamp"] = int(time.time())
    item["amount"] = Decimal("6.86")
    item["email"] = "<YOUR EMAIL ADDRESS HERE>"  # EDIT HERE
    item["album"] = {
        "artist_name": "Primus",
        "format": '12" Vinyl',
        "title": "Saiing the Seas of Cheese",
        "year": 1991,
    }
    response = table.put_item(Item=item)
except ClientError as e:
    print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
else:
    print(response)
