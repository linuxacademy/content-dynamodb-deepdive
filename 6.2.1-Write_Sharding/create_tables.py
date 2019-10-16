#!/usr/bin/env python3

import boto3

client = boto3.client("dynamodb")
votes = boto3.resource("dynamodb").Table("votes")

print(f"Creating raw_votes table")
response = client.create_table(
    TableName="raw_votes",
    KeySchema=[
        {"AttributeName": "voter_id", "KeyType": "HASH"},
        {"AttributeName": "timestamp", "KeyType": "RANGE"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "voter_id", "AttributeType": "S"},
        {"AttributeName": "timestamp", "AttributeType": "N"},
    ],
    BillingMode="PAY_PER_REQUEST",
)
print(response)

print(f"Creating votes table")
response = client.create_table(
    TableName="votes",
    KeySchema=[{"AttributeName": "segment", "KeyType": "HASH"}],
    AttributeDefinitions=[{"AttributeName": "segment", "AttributeType": "S"}],
    BillingMode="PAY_PER_REQUEST",
)
print(response)

print(f"Waiting for table votes...")
waiter = client.get_waiter("table_exists")
waiter.wait(TableName="votes")
response = client.describe_table(TableName="votes")
print(response["Table"]["TableStatus"])

print("Seeding votes table")
response = votes.put_item(Item={"segment": "Candidate A", "votes": 0})
print(response)
response = votes.put_item(Item={"segment": "Candidate B", "votes": 0})
print(response)

for i in range(1, 11):
    response = votes.put_item(Item={"segment": f"Candidate A_{i}", "votes": 0})
    print(response)
    response = votes.put_item(Item={"segment": f"Candidate B_{i}", "votes": 0})
    print(response)
