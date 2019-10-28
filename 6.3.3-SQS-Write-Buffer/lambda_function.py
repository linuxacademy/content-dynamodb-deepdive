import decimal
import json
import os

import boto3
from botocore.exceptions import ClientError

QUEUE_NAME = os.environ["QUEUE_NAME"]
DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]

sqs = boto3.resource("sqs")
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    print(
        "ApproximateNumberOfMessages:",
        queue.attributes.get("ApproximateNumberOfMessages"),
    )

    while True:
        for message in queue.receive_messages(MaxNumberOfMessages=10):
            item = json.loads(message.body, parse_float=decimal.Decimal)
            table = dynamodb.Table(DYNAMODB_TABLE)

            try:
                response = table.put_item(Item=item)
                print("Wrote message to DynamoDB:", json.dumps(response))
                message.delete()
                print("Deleted message:", message.message_id)
            except ClientError as e:
                print(
                    f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}'
                )
            else:
                print(response)
