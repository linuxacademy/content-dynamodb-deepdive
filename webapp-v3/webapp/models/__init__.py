import decimal
import os

import boto3

IS_OFFLINE = os.environ.get("IS_OFFLINE")

if IS_OFFLINE:
    dynamodb = boto3.client("dynamodb", endpoint_url="http://localhost:8000")
else:
    dynamodb = boto3.client("dynamodb")

pinehead_table = boto3.resource("dynamodb").Table("pinehead_records_s3")


def replace_decimals(obj):
    """ Because the Boto3 DynamoDB client turns all numeric types into Decimals
    (which is actually the right thing to do) we need to convert those
    Decimal values back into integers or floats before serializing to JSON.
    """
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
