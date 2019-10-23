#!/usr/bin/env python3

import argparse
import decimal
import json
import logging
import random
import sys
import time
import uuid

import boto3
from botocore.exceptions import ClientError
from faker import Faker


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


parser = argparse.ArgumentParser()
parser.add_argument("--queue-name", "-q", required=True, help="SQS queue name")
parser.add_argument(
    "--interval", "-i", required=True, help="timer interval", type=float
)
parser.add_argument("--log", "-l", default="INFO", help="logging level")
args = parser.parse_args()

if args.log:
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=args.log)

else:
    parser.print_help(sys.stderr)

sqs = boto3.client("sqs")

response = sqs.get_queue_url(QueueName=args.queue_name)

queue_url = response["QueueUrl"]

logging.info(queue_url)

while True:

    fake = Faker()
    item = {}
    item["id"] = str(uuid.uuid4())
    item["timestamp"] = int(time.time() * 1000)
    item["amount"] = decimal.Decimal(round(random.uniform(1.0, 50.0), 2))
    item["email"] = fake.email()
    item["album"] = {
        "artist_name": fake.name(),
        "format": random.choice(['7" Vinyl', '12" Vinyl']),
        "title": fake.sentence(3).split(".")[0].title(),
        "year": fake.year(),
    }

    message = json.dumps(item, cls=DecimalEncoder)

    logging.info("Sending message: " + message)

    try:
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=message)
        logging.info("MessageId: " + response["MessageId"])
    except ClientError as e:
        print(f'{e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')
    else:
        print(response)

    time.sleep(args.interval)
