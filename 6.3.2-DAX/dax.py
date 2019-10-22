#!/usr/bin/env python3

import argparse
import time

import boto3
from boto3.dynamodb.conditions import Attr

from amazondax import AmazonDaxClient

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--table-name", required=True, help="DynamoDB table name")
parser.add_argument("-k", "--track-name", required=True, help="Track (song) title")
parser.add_argument("-e", "--endpoint", help="DAX endpoint")
parser.add_argument("-i", "--iterations", type=int, default=5)
parser.add_argument("-v", "--verbose", action="store_true")
args = parser.parse_args()

if args.endpoint is not None:
    print("Using DAX")
    client = AmazonDaxClient(endpoint_url=args.endpoint)
else:
    print("Using DynamoDB without DAX")
    client = boto3.client("dynamodb")

table_name = args.table_name
track_name = args.track_name

start = time.time()

for i in range(args.iterations):
    print(f"Iteration {i}: Scanning '{table_name}' for track '{track_name}'")
    fe = "contains(track_information, :val)"
    eav = {":val": {"S": track_name}}
    response = client.scan(
        TableName=table_name, FilterExpression=fe, ExpressionAttributeValues=eav
    )

    if args.verbose:
        print(response)

    while "LastEvaluatedKey" in response:
        response = client.scan(
            TableName=table_name,
            FilterExpression=fe,
            ExpressionAttributeValues=eav,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )

        if args.verbose:
            print(response)

end = time.time()

print(
    "Total time: {} sec - Avg time: {} sec".format(
        end - start, (end - start) / args.iterations
    )
)
