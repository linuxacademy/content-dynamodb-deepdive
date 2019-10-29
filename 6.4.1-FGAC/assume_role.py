#!/usr/bin/env python3

import decimal
import json

import boto3
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

role_to_assume_arn = "arn:aws:iam::408073669315:role/LimitedDynamoDBRole"
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

# Create boto3 session with assumed role

session = boto3.Session(
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)

# Attempt scanning "user" table, which is *not* allowed by policy

try:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table("user")
    response = table.scan()
except ClientError as e:
    print("Error: %s" % e)

# Attempt GetItem on "pinehead_records_s3" table, which does *not* allow
# the "price" attribute

try:
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table("pinehead_records_s3")
    response = table.get_item(Key={"type": "album", "id": 15})
    print(json.dumps(response["Item"], cls=DecimalEncoder, indent=4))
except ClientError as e:
    print("Error: %s" % e)
