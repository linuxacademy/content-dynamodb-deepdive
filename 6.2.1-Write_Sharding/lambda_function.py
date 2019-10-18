"""
Run periodically, sum the values for each candidate segment, saving back
to the table as "Candidate A: total" and "Candidate B: total"
"""

import boto3

from botocore.exceptions import ClientError

print("Loading function")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("votes")


def lambda_handler(event, context):
    try:
        items = table.scan()["Items"]

        print(items)

        a = 0
        b = 0

        for i in items:
            if i["segment"].startswith("Candidate A_"):
                a = a + i["votes"]
            if i["segment"].startswith("Candidate B_"):
                b = b + i["votes"]

        print(f"Candidate A total: {a}")
        print(f"Candidate B total: {b}")

        table.update_item(
            Key={"segment": "Candidate A"},
            UpdateExpression="set votes = :v",
            ExpressionAttributeValues={":v": a},
        )

        table.update_item(
            Key={"segment": "Candidate B"},
            UpdateExpression="set votes = :v",
            ExpressionAttributeValues={":v": b},
        )

    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
    else:
        print("Aggregate totals updated")
