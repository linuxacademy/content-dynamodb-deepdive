import decimal

# import json

import boto3
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

print("Loading function")

table = boto3.resource("dynamodb").Table("votes")
td = TypeDeserializer()


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    sum_a = 0
    sum_b = 0

    for record in event["Records"]:
        # print(record["eventID"])
        # print(record["eventName"])
        # print("DynamoDB Record: " + json.dumps(record["dynamodb"], indent=2))

        data = record["dynamodb"].get("NewImage")
        d = {}
        for key in data:
            d[key] = td.deserialize(data[key])

        print(d)

        if d["candidate"] == "Candidate A":
            sum_a = sum_a + 1

        if d["candidate"] == "Candidate B":
            sum_b = sum_b + 1

    update_sum("Candidate A", sum_a)
    update_sum("Candidate B", sum_b)

    print("Successfully processed {} records.".format(len(event["Records"])))


def update_sum(candidate, sum):
    try:
        print(f"Updating aggregate votes for {candidate}. Sum: {sum}")

        table.update_item(
            Key={"segment": candidate},
            UpdateExpression="SET votes = votes + :val",
            ExpressionAttributeValues={":val": decimal.Decimal(sum)},
        )
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
        raise
    else:
        print("Aggregate votes updated")
