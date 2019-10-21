#!/usr/bin/env python3

"""Zero out all aggregate data in the votes table"""

import boto3

dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("votes")

response = table.scan()

for item in response["Items"]:
    response = table.update_item(
        Key={"segment": item["segment"]},
        UpdateExpression="SET votes = :v",
        ExpressionAttributeValues={":v": 0},
    )
