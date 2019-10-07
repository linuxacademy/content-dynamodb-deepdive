#!/bin/sh

# Create indexed version of album table
# GSI on title, LSI on format
# PK - aritst_id SK - id

aws dynamodb\
    create-table\
        --table-name album_indexed\
        --attribute-definitions\
            AttributeName=artist_id,AttributeType=N\
            AttributeName=id,AttributeType=N\
            AttributeName=format,AttributeType=S\
            AttributeName=title,AttributeType=S\
        --key-schema\
            AttributeName=artist_id,KeyType=HASH\
            AttributeName=id,KeyType=RANGE\
        --local-secondary-indexes\
            '[
                {
                    "IndexName": "alb_format",
                    "KeySchema": [
                        {
                            "AttributeName": "artist_id",
                            "KeyType": "HASH"
                        },
                        {
                            "AttributeName": "format",
                            "KeyType": "RANGE"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    }
                }
            ]'\
        --global-secondary-indexes\
            '[
                {
                    "IndexName": "alb_title",
                    "KeySchema": [
                        {
                            "AttributeName": "title",
                            "KeyType": "HASH"
                        }
                    ],
                    "Projection": {
                        "ProjectionType": "ALL"
                    }
                }
            ]'\
        --billing-mode PAY_PER_REQUEST