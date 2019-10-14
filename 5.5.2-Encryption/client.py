#!/usr/bin/env python3

import boto3
from boto3.dynamodb.types import Binary
from dynamodb_encryption_sdk.encrypted.table import EncryptedTable
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import (
    AwsKmsCryptographicMaterialsProvider,
)
from dynamodb_encryption_sdk.structures import AttributeActions

client = boto3.client("dynamodb")
existing_tables = client.list_tables()["TableNames"]
table_name = "secret_stuff"

if table_name not in existing_tables:
    print(f"Creating {table_name} table")
    response = client.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    print(f"Waiting for table session_data...")
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=table_name)

table = boto3.resource("dynamodb").Table(table_name)

# Create a KMS provider. Pass in a valid KMS customer master key.
aws_cmk_id = "1234abcd-12ab-34cd-56ef-1234567890ab"  # YOUR CMK HERE
aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmk_id)

# Tell the encrypted table to encrypt and sign all attributes except one.
actions = AttributeActions(
    default_action=CryptoAction.ENCRYPT_AND_SIGN,
    attribute_actions={"test": CryptoAction.DO_NOTHING},
)

# Use these objects to create an encrypted table resource.
encrypted_table = EncryptedTable(
    table=table, materials_provider=aws_kms_cmp, attribute_actions=actions
)

# Add an item to the table

plaintext_item = {
    "pk": "key1",
    "sk": "key2",
    "example": "data",
    "numbers": 42,
    "binary": Binary(b"\x0D\x0E\x0A\x0D\x0B\x0E\x0E\x0F"),
    "test": "don't encrypt me, bro!",
}

# Encrypt and sign item
encrypted_table.put_item(Item=plaintext_item)

index_key = {"pk": "key1", "sk": "key2"}

# Transparently verify and decrypt item
decrypted_item = encrypted_table.get_item(Key=index_key)["Item"]
print("Decrypted item:\n" + str(decrypted_item) + "\n")

# Get encrypted and signed item
encrypted_item = table.get_item(Key=index_key)["Item"]
print("Encrypted item:\n" + str(encrypted_item))

