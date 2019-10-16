#!/usr/bin/env python3

import time
import uuid
import random

import boto3
from botocore.exceptions import ClientError

client = boto3.client("dynamodb")
dynamodb = boto3.resource("dynamodb")
candidates = ["Candidate A"] * 5 + ["Candidate B"] * 4


def record_vote():
    try:

        candidate = random.choice(candidates)
        segment = candidate + "_" + str(random.randint(1, 10))

        print(f"Recording vote for {segment}")

        client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": "raw_votes",
                        "Item": {
                            "voter_id": {"S": str(uuid.uuid4())},
                            "candidate": {"S": candidate},
                            "timestamp": {"N": str(int(time.time()))},
                        },
                    }
                },
                {
                    "Update": {
                        "TableName": "votes",
                        "Key": {"segment": {"S": segment}},
                        "UpdateExpression": "SET votes = votes + :val",
                        "ExpressionAttributeValues": {":val": {"N": "1"}},
                    }
                },
            ]
        )

    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
    else:
        print("Vote recorded")


if __name__ == "__main__":
    for _ in range(1000):
        record_vote()
