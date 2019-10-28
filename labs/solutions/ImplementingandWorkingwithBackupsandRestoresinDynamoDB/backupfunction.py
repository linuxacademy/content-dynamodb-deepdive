import boto3
from datetime import datetime as date

print('Loading function...')

def lambda_handler(event, context):
    tables = ['PetInventory']
    ddbClient = boto3.client('dynamodb')
    results = {}

    for table in tables:
        try:
            timestamp = date.now().strftime("%b-%d-%Y-%H-%M-%S")
            ddbClient.create_backup(
                TableName = table,
                BackupName = f'{table}-{timestamp}'
            )
            results[table] = "success"
        except Exception as e:
            results[table] = e

    for k,v in results.items():
        print(f'{k}: {v}')
    
    return results