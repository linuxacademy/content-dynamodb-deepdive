#!/usr/bin/env python3

import decimal
import json

import boto3
from boto3.dynamodb.conditions import Key


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("album")

# When making a Query call, you use the KeyConditionExpression parameter to
# specify the hash key on which you want to query. If you want to use a
# specific index, you also need to pass the IndexName.

response = table.query(
    IndexName="artist_id-index",
    KeyConditionExpression=Key("artist_id").eq(192),  # 192 = Queen
    ProjectionExpression="title, price",
)

print("The query returned the following items:")
for i in response[u"Items"]:
    print(json.dumps(i, cls=DecimalEncoder))
