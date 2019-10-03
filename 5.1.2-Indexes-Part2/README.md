# 5.1.2 - Indexes: Part 2

```sh
aws dynamodb get-item \
    --table-name album \
    --index-name AlbumTitle-index \
    --key file://key.json \
    --projection-expression "title, price"
```

`key.json`:

```json
{
    "id": { "N": "2361441" }
}
```

Response:

```json
{
    "Item": {
        "price": {
            "N": "27.84"
        },
        "title": {
            "S": "La Malaguena"
        }
    }
}
```
