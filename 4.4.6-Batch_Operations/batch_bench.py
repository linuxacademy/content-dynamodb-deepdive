#!/usr/bin/env python3

from timeit import default_timer as timer

import boto3

dynamodb = boto3.resource("dynamodb")

ids = [
    1,
    4,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    15,
    16,
    17,
    18,
    20,
    22,
    23,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    34,
]

keys = []

[keys.append({"id": i}) for i in ids]

print("Using batch_get_item:")

start = timer()
for _ in range(20):
    dynamodb.meta.client.batch_get_item(RequestItems={"artist": {"Keys": keys}})
end = timer()
print(f"{end - start} seconds")

print("Using get_item:")
table = dynamodb.Table("artist")
start = timer()
for _ in range(20):
    for i in range(len(ids)):
        s = table.get_item(Key={"id": ids[i]})
end = timer()
print(f"{end - start} seconds")
