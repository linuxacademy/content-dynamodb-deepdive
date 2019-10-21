# Pinehead Records webapp v2

This version features:

- Better table structure (single hierarchical table)
- Local and Global secondary indexes
- Accounts in DynamoDB

## Issues to improve upon

- Search by track name still requires a full table scan

The following query methods from our application inform our indexes (see `models.py`):

- `Album.get_by_artist_id(artist_id)`
- `Album.find_by_artist(artist_name)`
- `Album.find_by_artist_ids(artist_ids)`
- `Album.find_by_title()`
- `Album.find_by_track()`
- `Artist.find_by_name()`
- `Track.get_by_album_id()`

## Table Info

| Name          | pinehead_records_s2 |
|---------------|---------------------|
| Partition Key | artist_name         |
| Sort Key      | id (album id)       |

## Indexes

| Type | Name                    | Partition Key | Sort Key | Attributes |
| -----|-------------------------|---------------|----------|----------- |
| LSI  | artist_name-title-index | artist_name   | title    | ALL        |
| LSI  | artist_name-year-index  | artist_name   | year     | ALL        |
| GSI  | format-index            | format        | -        | ALL        |
| GSI  | price-index             | price         | -        | ALL        |
| GSI  | title-index             | title         | -        | ALL        |
| GSI  | year-index              | year          | -        | ALL        |

## To create the v2 data model in your own account

```sh
aws configure set default.region us-east-1
pip3 install --user boto3
curl https://raw.githubusercontent.com/linuxacademy/content-dynamodb-deepdive/master/labs/bootstrap/tablebootstrap.py | python3 /dev/stdin -s 2 -f s3://dynamodblabs/pinehead_records_s2.csv
```
