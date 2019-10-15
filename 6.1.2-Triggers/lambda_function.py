import boto3
import json
import os

from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError

print("Loading function")

ses = boto3.client("ses")
td = TypeDeserializer()


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    for record in event["Records"]:
        print(record["eventID"])
        print(record["eventName"])
        print("DynamoDB Record: " + json.dumps(record["dynamodb"], indent=2))

        data = record["dynamodb"].get("NewImage")
        d = {}
        for key in data:
            d[key] = td.deserialize(data[key])

        print(d)

        send_email(d)

    print("Successfully processed {} records.".format(len(event["Records"])))


def send_email(data):
    SENDER = os.environ["SENDER"]
    CHARSET = "UTF-8"
    SUBJECT = "Pinehead Records: Order Confirmation"

    BODY_TEXT = (
        "Pinehead Records: Order Confirmation\r\n"
        f"Order ID: {data['id']}"
        f"Album: {data['album']['title']} ({data['album']['year']})"
        f"Format: {data['album']['format']}"
        f"Amount: {data['amount']}"
    )

    BODY_HTML = f"""<html>
    <head></head>
    <body>
    <h1>Pinehead Records: Order Confirmation</h1>
    <ul>
        <li>Order ID: {data['id']}</li>
        <li>Album: {data['album']['title']}</li>
        <li>Format: {data['album']['format']}</li>
        <li><b>Amount: {data['amount']}</b></li>
    </ul>
    </body>
    </html>
    """

    try:
        response = ses.send_email(
            Destination={"ToAddresses": [data["email"]]},
            Message={
                "Body": {
                    "Html": {"Charset": CHARSET, "Data": BODY_HTML},
                    "Text": {"Charset": CHARSET, "Data": BODY_TEXT},
                },
                "Subject": {"Charset": CHARSET, "Data": SUBJECT},
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])
