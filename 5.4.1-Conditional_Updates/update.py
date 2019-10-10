#!/usr/bin/env python3

import decimal

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("album")

try:
    response = table.put_item(
        Item={
            "id": 99887766,
            "artist_id": 88776655,
            "title": "Free Lunch",
            "year": "2019",
            "format": '12" Vinyl',
            # price is deliberately omitted
        }
    )
except ClientError as e:
    if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
        print(e.response["Error"]["Message"])
    else:
        raise
else:
    print("PutItem succeeded:")
    print(response)

# Update only if the item does not have a price attribute

try:
    response = table.update_item(
        Key={"id": 99887766},
        UpdateExpression="set price = :p",
        ExpressionAttributeValues={":p": decimal.Decimal(1.5)},
        ConditionExpression=Attr("price").not_exists(),
        ReturnValues="UPDATED_NEW",
    )

except ClientError as e:
    if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
        print(e.response["Error"]["Message"])
    else:
        raise
else:
    print("UpdateItem succeeded:")
    print(response)

# aws dynamodb get-item --table-name album --key {\"id\":{\"N\":\"99887766\"}}
# aws dynamodb delete-item --table-name album --key {\"id\":{\"N\":\"99887766\"}}
