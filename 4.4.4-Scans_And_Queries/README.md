# 4.4.4 - Scans and Queries

## Scan

### Filtering results

Sometimes you might need to write an expression containing an attribute name that conflicts with a DynamoDB reserved word. In this example, we replace `name` with an expression attribute name such as `#n`.

```sh
aws dynamodb scan --table-name artist \
    --filter-expression "#n = :name" \
    --expression-attribute-values '{":name":{"S":"Dream Theater"}}' \
    --expression-attribute-names '{"#n":"name"}'
```

Result:

```json
{
    "Items": [
        {
            "id": {
                "N": "154555"
            },
            "name": {
                "S": "Dream Theater"
            }
        }
    ],
    "Count": 1,
    "ScannedCount": 973696,
    "ConsumedCapacity": null
}
```

### Strongly Consistent Read

```sh
aws dynamodb scan --table-name artist \
    --filter-expression "#n = :name" \
    --expression-attribute-values '{":name":{"S":"Dream Theater"}}' \
    --expression-attribute-names '{"#n":"name"}' \
    --consistent-read
```

### Limit the number of items returned

```sh
aws dynamodb scan --table-name track --limit 3
```

Result:

```json
{
    "Items": [
        {
            "album_id": {
                "N": "1855173"
            },
            "length": {
                "N": "123000"
            },
            "id": {
                "N": "21662086"
            },
            "name": {
                "S": "Please Please Me"
            },
            "number": {
                "S": "A"
            }
        },
        {
            "album_id": {
                "N": "245766"
            },
            "length": {
                "N": "280000"
            },
            "id": {
                "N": "3424622"
            },
            "name": {
                "S": "Die rosarote Brille"
            },
            "number": {
                "N": "1"
            }
        },
        {
            "album_id": {
                "N": "1710199"
            },
            "length": {
                "N": "300000"
            },
            "id": {
                "N": "19937970"
            },
            "name": {
                "S": "Sofre"
            },
            "number": {
                "S": "B3"
            }
        }
    ],
    "Count": 3,
    "ScannedCount": 3,
    "LastEvaluatedKey": {
        "id": {
            "N": "19937970"
        }
    }
}
```

### Pagination

The `LastEvaluatedKey` in the response indicates that not all of the items have been retrieved. The AWS CLI then issues another `Scan` request to DynamoDB. This request and response pattern continues, until the final response.

```sh
aws dynamodb scan --table-name artist --page-size 10 --debug
```

## Query

### Find items based on primary key values

```sh
aws dynamodb query \
    --table-name artist \
    --key-condition-expression "id = :id" \
    --expression-attribute-values  '{":id":{"N":"154555"}}'
```

Result:

```json
{
    "Items": [
        {
            "id": {
                "N": "154555"
            },
            "name": {
                "S": "Dream Theater"
            }
        }
    ],
    "Count": 1,
    "ScannedCount": 1,
    "ConsumedCapacity": null
}
```
