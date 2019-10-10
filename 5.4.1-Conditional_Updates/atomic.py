#!/usr/bin/env python3

import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("album")

response = table.update_item(
    Key={"id": 28222},
    UpdateExpression="set in_stock = in_stock - :val",
    ExpressionAttributeValues={":val": 1},
    ReturnValues="UPDATED_NEW",
)

print("UpdateItem succeeded:")
print(response["Attributes"]["in_stock"])
