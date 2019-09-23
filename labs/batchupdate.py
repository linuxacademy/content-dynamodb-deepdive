import boto3

ddbClient = boto3.client('dynamodb')

recordsToUpdate = ddbClient.scan(
    TableName = 'PetInventory',
    AttributesToGet = [
        'pet_species',
        'pet_id'
    ]
)['Items']

for record in recordsToUpdate:
    try:
        if record['pet_species']['S'] == 'Monitor Lizard':
            updateVal = False
        else:
            updateVal = True
        updateResponse = ddbClient.update_item(
            ExpressionAttributeValues={
                ':pa': {'BOOL': updateVal}
            },
            UpdateExpression='SET pet_available = :pa',
            Key = record,
            ReturnValues = 'NONE',
            TableName = 'PetInventory'
        )
    except Exception as e:
        print(e)