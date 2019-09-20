import boto3

ddb = boto3.client('dynamodb')
scanItems = ddb.scan(TableName = 'PetInventory')['Items']

labels = {'species': 'Species', 'id': 'ID', 'name': 'Name', 'color': 'Color', 'age': 'Age', 'gender':'Gender', 'furscale': 'Fur Type/Scale Texture'}
print(f"{labels['species']:^20}{labels['id']:^20}{labels['name']:^20}{labels['color']:^20}{labels['age']:^20}{labels['gender']:^20}{labels['furscale']:^30}")

for item in scanItems:
    itemValues = {}
    for key, value in item.items():
        if key == 'scale_texture' or key == 'fur_type':
            key = 'furscale'
        val = list(value.values())
        itemValues[key] = val[0]
    print(f"{itemValues['pet_species']:^20}{itemValues['pet_id']:^20}{itemValues['name']:^20}{itemValues['color']:^20}{itemValues['age']:^20}{itemValues['gender']:^20}{itemValues['furscale']:^30}")