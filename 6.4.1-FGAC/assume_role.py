#!/usr/bin/env python3

import decimal
import json

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError


# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


sts = boto3.client("sts")

print("Default Provider Identity: : " + sts.get_caller_identity()["Arn"])

# Replace with ARN of your limited DynamoDB role:
role_to_assume_arn = "arn:aws:iam::123456789012:role/LimitedDynamoDBRole"
role_session_name = "test_session"

response = sts.assume_role(
    RoleArn=role_to_assume_arn, RoleSessionName=role_session_name
)

creds = response["Credentials"]

sts_assumed_role = boto3.client(
    "sts",
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)

print("AssumedRole Identity: " + sts_assumed_role.get_caller_identity()["Arn"])

# Create boto3 client with assumed role

dynamodb = boto3.client(
    "dynamodb",
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)

# Attempt scanning "user" table, which is *not* allowed by policy

try:
    response = dynamodb.scan(TableName="users")
except ClientError as e:
    print("Error: %s" % e)

# Attempt query on "pinehead_records_s3" table, which does *not* allow
# the "price" attribute. Adding "price" to the ProjectionExpression will
# result in an error.

session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)

dynamodb = session.resource("dynamodb")

try:

    table = dynamodb.Table("pinehead_records_s3")

    response = table.query(
        KeyConditionExpression=Key("type").eq("album") & Key("id").eq(15),
        ProjectionExpression="#T, id, name_title",
        # ProjectionExpression="#T, id, name_title, price",  # AccessDeniedException
        ExpressionAttributeNames={"#T": "type"},
    )

    print(json.dumps(response["Items"][0], cls=DecimalEncoder, indent=4))
except ClientError as e:
    print("Error: %s" % e)
