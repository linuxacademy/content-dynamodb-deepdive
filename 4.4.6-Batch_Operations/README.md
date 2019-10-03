# 4.4.6 - Batch Operations

## BatchGetItem

```sh
aws dynamodb batch-get-item --request-items file://get.json
```

Response

```json
{
    "Responses": {
        "artist": [
            {
                "id": {
                    "N": "5135"
                },
                "name": {
                    "S": "Fates Warning"
                }
            },
            {
                "id": {
                    "N": "192"
                },
                "name": {
                    "S": "Queen"
                }
            },
            {
                "id": {
                    "N": "154555"
                },
                "name": {
                    "S": "Dream Theater"
                }
            }
        ]
    },
    "UnprocessedKeys": {}
}
```

## BatchWriteItem

```sh
aws dynamodb batch-write-item --request-items file://write.json
```

Response

```json
{
    "UnprocessedItems": {}
}
```
